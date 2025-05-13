import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm

load_dotenv()
API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=API_KEY)

with open("skku_notices.json", "r", encoding="utf-8") as f:
    notices = json.load(f)

result = []

for notice in tqdm(notices, desc="공지별 검색질문 생성"):
    notice_id = notice["id"]
    title = notice["title"]
    content = notice["content"]
    prompt = (
        "아래는 대학 공지사항의 제목과 내용입니다.\n"
        f"제목: {title}\n"
        f"내용: {content}\n"
        "이 공지사항을 찾으려는 학생이 실제로 검색창에 입력할 법한 구체적이고 자연스러운 질문을 한국어로 5개 만들어줘. "
        "예를 들어, 'SK희망메이커 멘토 모집 일정 알려줘', 'SK 멘토 봉사 혜택 뭐야?'처럼, "
        "공지의 주요 정보(일정, 지원자격, 혜택, 신청방법 등)를 찾으려는 학생의 입장에서 작성해줘. 질문만 리스트로 출력해줘."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "공지사항을 찾으려는 학생이 검색창에 입력할 법한 구체적인 질문을 5개 리스트로 만들어주세요."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=300,
        temperature=0.7,
    )
    content = response.choices[0].message.content.strip()
    questions = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if line[0].isdigit() or line.startswith("-"):
            q = line.split(".", 1)[-1].strip() if "." in line else line.lstrip("-").strip()
            if q:
                questions.append(q)
    if len(questions) < 5:
        questions = [l.strip("-").strip() for l in content.splitlines() if l.strip()]
    result.append({
        "id": notice_id,
        "query": questions[:5]
    })

with open("skku_notice_queries.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
