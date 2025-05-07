import crawling, generate_query, bm25

import numpy as np
from sklearn.metrics import accuracy_score
import argparse, sys

def 

def eval():
    k = 3               # hit을 판단할 top-k
    hit_cnt = 0
    total_cnt = 0

    query = generate_query.get_query()

    for id in generated_query.keys():
        for query in generated_query[id]['query_list']:
            tokenized_query = preprocess(query)
            doc_scores = bm25.get_scores(tokenized_query)

            pred = []
            pred_idx = np.argsort(doc_scores)[-k:]

            for idx in pred_idx:
                pred.append(corpus_data_mapping[idx])
            
            if id in pred:
                hit_cnt += 1
            total_cnt += 1

    print(f"hit_cnt {hit_cnt}")
    print(f"total_cnt {total_cnt}")
    print(f"hit_rate {hit_cnt/total_cnt}")


def main(mode):
    if mode == 'eval':



if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('-mode', help=' : running mode (eval, conversation)') 
    

    args = parser.parse_args()

    if args.mode not in ['eval', 'conversation']:
        print('invalid argument')
        exit(1)

    main(args.mode)