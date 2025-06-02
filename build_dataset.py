import os
import json
import pandas as pd

# train.csv
# corpus.json
# 구성
def build_dataset(data, response):
    corpus = {}
    queries = []
    responses = []
    
    for e in data:
        corpus[e['id']] = e['content']
    
    for e in response:
        queries.append(e['query'])
        response.append(e['response'])

    df = pd.DataFrame({
        'query': queries,
        'response': responses
    })
    df.to_csv('query_response.csv', index=False)

    json_data = json.dumps(corpus, indent=4, ensure_ascii=False)
    with open("Dataset/corpus.json", "w", encoding="utf-8") as f:
        f.write(json_data)
        
