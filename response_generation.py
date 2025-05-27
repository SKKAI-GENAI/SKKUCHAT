import os
from dotenv import load_dotenv
import random
import json
from tqdm import tqdm
import jsonschema

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 답변 형식
response_schema = {
    "type": "object",
    "title": "Query-Responses",
    "description": "Schema for the response containing list of queries.",
    "properties": {
        "response": {"type": "string"}
    },
}

# load api key, need .env file
load_dotenv()

# prompt + model + output parser
prompt = ChatPromptTemplate.from_template("너는 성균관대학교 공지사항 챗봇이고, 학생은 특정한 공지사항에 대해 질문을 할거야. 너는 질문이 주어지면 질문에 해당하는 공지사항을 찾은 후, 공지사항을 가지고 질문에 대한 대답을 해야해. 다행이도 너에겐 질문에 해당하는 공지사항의 제목과 내용이 주어질거야. 그래서, 다음으로 학생의 질문과 질문에 해당하는 공지사항의 제목과 내용이 주어지면, 공지사항을 가지고 질문에 대해 적절한 답을 해줘. 참고로 이건 챗봇 모델 학습에 쓰일 데이터 생성을 위한 질문이기 때문에, 답변을 모델의 label로 사용되기 적절하게 생성해줬으면 좋겠어. 질문: {query} \n공지사항 제목: {title} \n공지사항 내용: {content}")
llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(response_schema)

# LCEL chaining
chain = prompt | llm

def generate_response(data, query):
    if os.path.isfile('Dataset/response_gen.json'):
        return

    # chain 호출
    generated_response = []
    print("generating response...")
    for e in tqdm(data):
        for e1 in query:
            if e1['id'] == e['id']:
                for q in e1['query']:
                    generated_response.append({
                        'id':e['id'], 
                        'query':q,
                        'response':chain.invoke({"query":q ,"title": e['title'], "content":e['content']})['response']
                        })

    json_data = json.dumps(generated_response, indent=4, ensure_ascii=False)

    with open("Dataset/response_gen.json", "w", encoding="utf-8") as f:
        f.write(json_data)

def get_response():
    with open('Dataset/response_gen.json', 'r', encoding='utf-8') as f:
        generated_response = json.load(f)
    
    if not generated_response:
        print('data error: first run run.py as prepare mode')
        exit(1)

    return generated_response
