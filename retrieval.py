import sqlite3
from typing import List, Tuple, Dict, NoReturn, Optional

import torch
import numpy as np
import pandas as pd # ?

from utils.Preprocessor import Preprocess_text # based on Mecab

from rank_bm25 import BM25Okapi

# https://huggingface.co/Dongjin-kr/ko-reranker
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class SparseRetrieval:
    def __init__(self) -> NoReturn:
        # 데이터베이스 연결
        conn = sqlite3.connect("./data/notices.db")
        cur = conn.cursor()

        # 데이터 로딩
        self.corpus = []
        self.corpus_info = []

        cur.execute("SELECT * FROM notices")
        rows = cur.fetchall()
        for row in rows:
            self.corpus.append(row[2]) # content (전처리 완료)
            self.corpus_info.append(
                {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                }
            )
        conn.close()

        # BM25 객체 생성
        self.bm25 = BM25Okapi(self.corpus)

        # ko-reranker 모델 및 토크나이저 로딩
        self.reranker_tokenizer = AutoTokenizer.from_pretrained("Dongjin-kr/ko-reranker")
        self.reranker_model = AutoModelForSequenceClassification.from_pretrained("Dongjin-kr/ko-reranker")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.reranker_model.to(self.device)

    def get_relevant_doc(self, query: str, topk: Optional[int] = 1) -> List[int]:
        # 쿼리 전처리
        preprocessed_query = Preprocess_text(query)

        # BM25 랭킹
        doc_scores = self.bm25.get_scores(preprocessed_query)
        doc_indices = np.argsort(doc_scores)[::-1][:topk]
        return doc_indices.tolist()

    def _rerank(self, pairs: List[List[str]]) -> List[float]:
        with torch.no_grad():
            inputs = self.reranker_tokenizer(
                pairs, padding=True, truncation=True, return_tensors="pt"
            ).to(self.device)
            logits = self.reranker_model(**inputs).logits.squeeze(-1).cpu().tolist()
        return logits

    def retrieve(
        self, query: str, topk: Optional[int] = 1,
        threshold: Optional[float] = -3  # rerank logit 임계값
    ) -> List[Tuple[float, Dict]]:
        # BM25 랭킹 (1차로 topk * 5만큼 후보군 선정)
        doc_indices = self.get_relevant_doc(query, topk * 5)

        # 쿼리-문서 쌍 생성
        passages = [self.corpus[i] for i in doc_indices]
        pairs = [[query, passage] for passage in passages]

        # Reranking
        rerank_logits = self._rerank(pairs)

        # top-k 중 threshold 이상만 필터링
        filtered = [
            (rerank_logits[i], doc_indices[i]) 
            for i in np.argsort(rerank_logits)[::-1] 
            if rerank_logits[i] >= threshold
        ]

        results = [(logit, self.corpus_info[idx]) for logit, idx in filtered]
        return results
