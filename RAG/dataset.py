import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import bm25, crawling, query_generation
import json
from torch.utils.data import Dataset
from transformers import AutoTokenizer

class SKCTDataset(Dataset):
    def __init__(self, csv_path, corpus_csv_path, k, tokenizer_name='skt/kobert-base-v1', max_input_length=512, max_output_length=512):
        self.data = pd.read_csv(csv_path)
        with open(corpus_csv_path, 'r', encoding='utf-8') as f:
            self.corpus = json.load(f)
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.max_input_length = max_input_length
        self.max_output_length = max_output_length

        # data에 retrieved document k개 추가
        bm25_model = bm25.BM25(crawling.get_data(), query_generation.get_query())

        retrieved_document_topk = {}
        for e in data:
            retrieved_document_ids = bm25_model.retrieve_topk(data['query'], k)
            for topi, id in enumerate(retrieved_document_ids):
                retrieved_document_topk[topi] = corpus[id]
            
        for

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        query = self.data.loc[idx, 'query']
        response = self.data.loc[idx, 'response']

        input_encoding = self.tokenizer(
            query,
            truncation=True,
            padding='max_length',
            max_length=self.max_input_length,
            return_tensors='pt'
        )

        target_encoding = self.tokenizer(
            response,
            truncation=True,
            padding='max_length',
            max_length=self.max_output_length,
            return_tensors='pt'
        )

        labels = target_encoding['input_ids']
        labels[labels == self.tokenizer.pad_token_id] = -100  # ignore padding tokens in loss

        return {
            'input_ids': input_encoding['input_ids'].squeeze(0),
            'attention_mask': input_encoding['attention_mask'].squeeze(0),
            'labels': labels.squeeze(0)
        }
