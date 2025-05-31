from generator.t5 import KoBARTGenerator
from dataset import SKCTDataset

class RAGPipeline:
    def __init__(self):
        self.generator = KoBARTGenerator()
        self.dataset = SKCTDataset()

    def generate(self, input):
        query = self.dataset(input) #여기서 데이터 corpus랑 input 합쳐져서 반환되게
        output = self.generator.generate_from_text(query)
        return output



if __name__ == "__main__":
    rag = RAGPipeline()

    while True:
        q = input("\n질문을 입력하세요 (종료: 'exit'): ")
        if q.lower() == "exit":
            break

        answer = rag.generate(q)
        print("응답:", answer)
