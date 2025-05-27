from retriever.bm25 import BM25Retriever
from generator.kobart import KoBARTGenerator

class RAGPipeline:
    def __init__(self, corpus):
        self.retriever = BM25Retriever(corpus)
        self.generator = KoBARTGenerator()

    def generate(self, query):
        context = self.retriever.retrieve(query)
        return self.generator.generate(query, context)



if __name__ == "__main__":