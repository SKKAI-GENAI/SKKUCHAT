import json
import os
import time
from typing import List, NoReturn, Optional, Tuple, Union

import numpy as np
import pandas as pd
from datasets import Dataset
from tqdm.auto import tqdm
from rank_bm25 import BM25Okapi

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

        self.p_embedding = None  # get_sparse_embedding()로 생성합니다
        self.indexer = None  # build_faiss()로 생성합니다.
        self.embedding_ready = False
        
    
    def get_sparse_embedding(self) -> NoReturn:
        print("BM25Okapi 모델 사용 중, 별도의 임베딩이 필요하지 않습니다.")
        self.embedding_ready = True  # 임베딩이 준비되었다는 플래그 설정

    def retrieve(
        self, query_or_dataset: Union[str, Dataset], topk: Optional[int] = 1
    ) -> Union[Tuple[List, List], pd.DataFrame]:
        assert self.embedding_ready, "get_sparse_embedding() 메소드를 먼저 수행해줘야합니다."

        if isinstance(query_or_dataset, str):
            doc_scores, doc_indices = self.get_relevant_doc(query_or_dataset, topk)

            # id 반환을 위해 doc_indices를 self.ids로 매핑
            retrieved_ids = [self.notice_ids[i] for i in doc_indices]

            return (doc_scores, retrieved_ids)

    def get_relevant_doc(self, query: str, topk: int) -> Tuple[List[float], List[int]]:
        # ---------------------------- vanilla ---------------------------
        tokenized_query = self.tokenize_fn(query)
        doc_scores = self.bm25.get_scores(tokenized_query)
        doc_indices = np.argsort(doc_scores)[::-1][:topk]
        return doc_scores[doc_indices].tolist(), doc_indices.tolist()
    
        # --------------------------- rerank --------------------------------
        #tokenized_query = self.tokenize_fn(query)
        #doc_scores = self.bm25.get_scores(tokenized_query)
        #doc_indices = np.argsort(doc_scores)[::-1][:topk*2]
          
        #initial_contexts = [self.contexts[i] for i in doc_indices]
        #selected_scores = [doc_scores[i] for i in range(len(doc_indices))]
        #reranked_scores, reranked_contexts = self.rerank(query, initial_contexts, selected_scores, topk)
        #reranked_indices = [self.contexts.index(context) for context in reranked_contexts]
        
        #return reranked_scores.tolist(), reranked_indices
    