import bm25

import os
import json
from tqdm import tqdm

def generate_response(data, response):
    for e in t

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

    with open("response_gen.json", "w", encoding="utf-8") as f:
        f.write(json_data)

def get_response():
    with open('response_gen.json', 'r', encoding='utf-8') as f:
        generated_response = json.load(f)
    
    if not generated_response:
        print('data error: first run run.py as prepare mode')
        exit(1)

    return generated_response
