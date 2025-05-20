import crawling, query_generation, bm25, response_generation

import numpy as np
from sklearn.metrics import accuracy_score
import argparse, sys

# 데이터 크롤링
# 쿼리 생성
def prepare_bm25():
    crawling.crawl_skku_notice()
    query_generation.generate_query(crawling.get_data())

# hit rate 계산
def eval_bm25(k):
    data = crawling.get_data()
    query = query_generation.get_query()
    model = bm25.BM25(data, query)

    hit_rate = model.get_hitrate(k)

    print(f"hit rate: {hit_rate}")

def prepare_rag():
    prepare_bm25()
    response_generation.generate_response(crawling.get_data(), query_generation.get_query())

def main(args):   
    if args.model == 'bm25':
        if args.mode == 'prepare':              # prepare
            prepare_bm25()
        elif args.mode == 'eval':             # bm25 eval
            eval_bm25(args.k)
        elif args.mode == 'conversation':   # bm25 demo
            # demo
            exit(1)
        else:
            print('invalid argument')
            exit(1)
    elif args.model == 'rag':
        if args.mode == 'prepare':
            prepare_rag()

# 사용법
# python run.py -mode MODE -model MODEL -k K
# python run.py -mode=MODE -model=MODEL -k=K
if __name__ == '__main__' :
    parser = argparse.ArgumentParser()
    parser.add_argument('-mode', help=' : running mode (prepare, train, eval, conversation)') 
    parser.add_argument('-model', help=' : select model (bm25, rag)')
    parser.add_argument('-k', type=int, help=' : top-k in evaluation', default=3) 

    # argument valid check
    args = parser.parse_args()
    if args.mode not in ['prepare', 'train', 'eval', 'conversation']:           
        print('invalid argument')
        exit(1)

    main(args)