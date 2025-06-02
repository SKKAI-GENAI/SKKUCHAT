import preprocess

import numpy as np
from tqdm import tqdm
from rank_bm25 import BM25Okapi

class BM25:
    def __init__(self, data, query=None, k1=1.2, b=0.75):
        self.data = data
        self.query = query
        self.k1 = k1
        self.b = b

        self.corpus = []
        self.corpus_id_mapping = {}
        for i, e in enumerate(self.data):
            self.corpus.append(preprocess.process(e['content']))
            self.corpus_id_mapping[i] = e['id']
        
        self.bm25 = BM25Okapi(self.corpus)
    
    def get_hitrate(self, k):
        hit_cnt = 0
        total_cnt = 0

        print("evaluating with bm25...")
        for q_dict in tqdm(self.query):
            id = q_dict['id']
            q_list = q_dict['query']
            for q in q_list:
                # preprocess and get score
                p_q = preprocess.process(q)
                doc_scores = self.bm25.get_scores(p_q)

                pred = []
                pred_idx = np.argsort(doc_scores)[-k:]

                for idx in pred_idx:
                    pred.append(self.corpus_id_mapping[idx])

                if id in pred:
                    hit_cnt += 1
                total_cnt += 1

        print(hit_cnt)
        print(total_cnt)
        return hit_cnt/total_cnt
    
    def retrieve(q):
        p_q = preprocess.process(q)
        doc_scores = self.bm25.get_scores(p_q)

        pred_idx = np.argsort(doc_scores)[-1]

        return self.corpus_id_mapping[pred_idx]

    def retrieve_topk(q, k):
        p_q = preprocess.process(q)
        doc_scores = self.bm25.get_scores(p_q)

        pred = []
        pred_idx = np.argsort(doc_scores)[-k:]

        for idx in pred_idx:
            pred.append(self.corpus_id_mapping[idx])

        return pred

        


