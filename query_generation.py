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
        "query": {"type": "array", "items": {"type": "string"}}
    },
}

# load api key, need .env file
load_dotenv()

# prompt + model + output parser
prompt = ChatPromptTemplate.from_template("너는 찾고 싶은 학과 공지사항이 있는 성균관대학교 학부생이고, 학교 챗봇에 질문을 통해 그 공지사항을 찾으려고 할거야. 다음으로 너가 찾고 싶은 공지사항의 제목과 내용이 주어지면 해당 공지사항을 찾기 위해 챗봇에게 질문할 적절한 쿼리 5개를 생성해줘. 제목: {title} 내용: {content}")
llm = ChatOpenAI(model="gpt-4o-mini").with_structured_output(response_schema)

# LCEL chaining
chain = prompt | llm

def generate_query(data):
    # chain 호출
    generated_query = []
    print("generating query...")
    for e in tqdm(data):
        generated_query.append({
            'id':e['id'], 
            'query':chain.invoke({"title": e['title'], "content":e['content']})['query']
            })

    json_data = json.dumps(generated_query, indent=4, ensure_ascii=False)

    with open("query_gen.json", "w", encoding="utf-8") as f:
        f.write(json_data)

def get_query():
    with open('query_gen.json', 'r', encoding='utf-8') as f:
        generated_query = json.load(f)
    
    if not generated_query:
        print('data error: first run run.py as prepare mode')
        exit(1)

    return generated_query
