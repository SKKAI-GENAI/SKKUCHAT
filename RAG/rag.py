from bm25 import BM25
from generator.t5 import KoT5Generator
import json

class RAGPipeline:
    def __init__(self, corpus_path):
        with open(corpus_path, 'r', encoding='utf-8') as f:
            corpus = json.load(f)
        self.corpus = {item['id']: item for item in corpus}
        self.retriever = BM25(self.corpus)
        self.generator = KoT5Generator()

    def generate(self, query):
        docs = self.retriever.retrieve_topk(query, k=3)
        context = ""
        for i, doc_idx in enumerate(docs):
            doc = self.corpus[doc_idx]
            title = doc.get("title", "")
            content = doc.get("content", "")
            context += f" Document{i+1}: {title}. {content}"

        input = f"Query: {query}, Document: {context}"
        output = self.generator.generate_from_text(input)
        return output



if __name__ == "__main__":
    corpus_path = ""
    rag = RAGPipeline(corpus_path)

    while True:
        q = input("\n질문을 입력하세요 (종료: 'exit'): ")
        if q.lower() == "exit":
            break

        answer = rag.generate(q)
        print("응답:", answer)
