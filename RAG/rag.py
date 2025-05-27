from retriever.bm25 import BM25Retriever
from generator.t5 import KoBARTGenerator
from dataset import SKCTDataset

class RAGPipeline:
    def __init__(self, corpus):
        self.retriever = BM25Retriever(corpus)
        self.generator = KoBARTGenerator()
        self.dataset = SKCTDataset()

    def generate(self, input):
        context = self.retriever.retrieve(input)
        query = self.dataset(input, context)
        output = self.generator.generate_from_text(query)
        return output



if __name__ == "__main__":
    corpus = 
    rag = RAGPipeline(corpus)

    while True:
        q = input("\n질문을 입력하세요 (종료: 'exit'): ")
        if q.lower() == "exit":
            break

        answer = rag.generate(q)
        print("응답:", answer)
