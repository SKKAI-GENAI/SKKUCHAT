import json
from tqdm import tqdm
from konlpy.tag import Okt
from retrieval import SparseRetrieval  # 기존 SparseRetrieval 클래스 import

# 1. 데이터 로드
with open("skku_notice_queries.json", "r", encoding="utf-8") as f:
    queries_data = json.load(f)
with open("skku_notices.json", "r", encoding="utf-8") as f:
    notices_data = json.load(f)

# 2. notice id -> context 매핑
notice_id2context = {notice["id"]: notice["content"] for notice in notices_data}

# 3. 질문-정답 쌍 생성
eval_samples = []
for entry in queries_data:
    notice_id = entry["id"]
    for q in entry["query"]:
        eval_samples.append({"id": notice_id, "question": q})

# 4. SparseRetrieval 인스턴스 준비
retriever = SparseRetrieval(context_path="skku_notices.json", tokenize_fn= Okt().morphs)  # SparseRetrieval 인스턴스 생성
retriever.get_sparse_embedding()  # BM25 임베딩 준비 메서드 호출

# 5. 평가 및 hitrate 계산
topk = 3
hit_counts = {sample["id"]: 0 for sample in eval_samples}  # id별 hit 카운트 초기화

total_queries = len(eval_samples)
for sample in tqdm(eval_samples, desc="BM25 notice hit@k 평가"):
    q = sample["question"]
    gt_id = sample["id"]
    _, retrieved_ids = retriever.retrieve(q, topk=topk)  # retrieve 메서드 호출
    if gt_id in retrieved_ids:
        hit_counts[gt_id] += 1
total_hits = sum(hit_counts.values())
# hitrate 계산 및 저장
output_file = "hitrate_results.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for notice_id, hit_count in hit_counts.items():
        hitrate = hit_count / 5
        f.write(f"Notice ID: {notice_id}, Hitrate: {hitrate:.3f}\n")
    f.write(f"Total Hitrate: {total_hits / total_queries:.3f}\n")
print(f"Hitrate 결과가 {output_file} 파일에 저장되었습니다.")
