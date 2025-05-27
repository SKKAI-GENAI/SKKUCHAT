import json
import os
import time
from typing import List, NoReturn, Optional, Tuple, Union

import numpy as np
import pandas as pd
from datasets import Dataset
from tqdm.auto import tqdm
from rank_bm25 import BM25Okapi

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


def timer(name):
    t0 = time.time()
    yield
    print(f"[{name}] done in {time.time() - t0:.3f} s")


class SparseRetrieval:
    def __init__(
        self,
        tokenize_fn,
        context_path: Optional[str] = "skku_notices.json",
    ) -> NoReturn:
        self.tokenize_fn = tokenize_fn
        self.context_path = context_path
        full_path = os.path.join(os.getcwd(), context_path)
        with open(full_path, "r", encoding="utf-8") as f:
            notice = json.load(f)
            self.contexts = []
            self.notice_ids = []
            self.titles = []
            self.urls = []
            for v in notice:
                if v["content"] not in self.contexts:
                    self.contexts.append(v["content"])
                    self.notice_ids.append(v["id"])
                    self.titles.append(v.get("title", "제목 없음"))
                    self.urls.append(v.get("url", ""))

        # 텍스트 토크나이징
        self.tokenized_contexts = [tokenize_fn(doc) for doc in self.contexts]
        # BM25 객체 생성
        self.bm25 = BM25Okapi(self.tokenized_contexts)

        self.p_embedding = None
        self.indexer = None
        self.embedding_ready = False

        # ko-reranker 모델 및 토크나이저 로딩
        self.reranker_tokenizer = AutoTokenizer.from_pretrained("Dongjin-kr/ko-reranker")
        self.reranker_model = AutoModelForSequenceClassification.from_pretrained("Dongjin-kr/ko-reranker")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.reranker_model.to(self.device)

    def get_sparse_embedding(self) -> NoReturn:
        print("BM25Okapi 모델 사용 중, 별도의 임베딩이 필요하지 않습니다.")
        self.embedding_ready = True

    def get_relevant_doc(self, query: str, topk: int) -> Tuple[List[float], List[int]]:
        tokenized_query = self.tokenize_fn(query)
        doc_scores = self.bm25.get_scores(tokenized_query)

        exp_scores = np.exp(doc_scores)
        softmax_scores = exp_scores / np.sum(exp_scores)

        doc_indices = np.argsort(softmax_scores)[::-1][:topk]
        return softmax_scores[doc_indices].tolist(), doc_indices.tolist()

    def _rerank(self, query_doc_pairs: List[Tuple[str, str]]) -> List[float]:
        inputs = self.reranker_tokenizer(
            [q for q, d in query_doc_pairs],
            [d for q, d in query_doc_pairs],
            padding=True,
            truncation=True,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.reranker_model(**inputs)
            scores = outputs.logits.squeeze(-1).cpu().tolist()

        return scores

    def retrieve(
        self, query_or_dataset: Union[str, Dataset], topk: Optional[int] = 1,
        threshold: Optional[float] = -4  # rerank 점수 기준
    ) -> Union[Tuple[List, List], pd.DataFrame]:
        assert self.embedding_ready, "get_sparse_embedding() 메소드를 먼저 수행해줘야 합니다."

        if isinstance(query_or_dataset, str):
            initial_topk = topk * 5
            doc_scores, doc_indices = self.get_relevant_doc(query_or_dataset, initial_topk)

            query = query_or_dataset
            passages = [self.contexts[i] for i in doc_indices]
            pairs = [(query, passage) for passage in passages]

            rerank_scores = self._rerank(pairs)
            sorted_indices = np.argsort(rerank_scores)[::-1]

            # top-k 중 threshold 이상만 필터링
            filtered = [(rerank_scores[i], doc_indices[i]) for i in sorted_indices if rerank_scores[i] >= threshold]
            if len(filtered) == 0:
                return [], []

            #final = filtered[:topk]
            final_scores = [score for score, _ in filtered]
            final_doc_indices = [idx for _, idx in filtered]
            retrieved_ids = [self.notice_ids[i] for i in final_doc_indices]

            return final_scores, retrieved_ids
