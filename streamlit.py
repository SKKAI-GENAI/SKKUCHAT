import streamlit as st
from konlpy.tag import Okt
from dotenv import load_dotenv
import os
import openai
from retrieval import SparseRetrieval
import subprocess
import json

# 환경 변수 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit 설정
st.set_page_config(page_title="스꾸챗 - 성균관대 챗봇", page_icon="🤖")
st.title("🦁 스꾸챗: 성균관대 공지사항 챗봇")

# 세션 상태 초기화
if "chat" not in st.session_state:
    st.session_state["chat"] = []

# Retriever 캐시로 불러오기
@st.cache_resource
def load_retriever():
    try:
        subprocess.run(["python3", "crawl_notice.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while running crawl_notice.py: {e}")
        return []
    try:
        with open("skku_notices.json", "r", encoding="utf-8") as f:
            notices = json.load(f)
    except FileNotFoundError:
        print("skku_notices.json not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding skku_notices.json: {e}")
        return []

    retriever = SparseRetrieval(tokenize_fn=Okt().morphs, context_path="skku_notices.json")
    retriever.get_sparse_embedding()
    return retriever

retriever = load_retriever()

# 첫 인삿말
if not st.session_state["chat"]:
    with st.chat_message("assistant"):
        st.write("안녕하세요! 저는 성균관대학교 공지사항 챗봇, 스꾸챗입니다. 궁금한 점을 물어보세요!")

# 기존 대화 히스토리 출력
for role, msg in st.session_state["chat"]:
    with st.chat_message(role):
        st.write(msg)

# 사용자 질문 입력
prompt = st.chat_input("성균관대 관련 궁금한 공지를 입력해보세요!")

if prompt:
    # 사용자 질문 추가
    st.session_state["chat"].append(("user", prompt))
    st.chat_message("user").write(prompt)

    # 관련 공지 추출
    scores, notice_ids = retriever.retrieve(prompt, topk=3)
    title_url_pairs = []
    for nid in notice_ids:
        idx = retriever.notice_ids.index(nid)
        title = retriever.titles[idx]
        url = f"https://www.skku.edu/skku/campus/skk_comm/notice01.do?mode=view&articleNo={int(nid)}"
        title_url_pairs.append((title, url))
    title_url_text = "\n".join([f"{i+1}. {title} {url}" for i, (title, url) in enumerate(title_url_pairs)])

    with st.chat_message("assistant"):
        st.write("🔎 관련 공지를 찾았어요:\n")
        st.write(title_url_text)
        st.write(scores)

    st.session_state["chat"].append(("assistant", "🔎 관련 공지를 찾았어요:\n" + title_url_text))

    # GPT 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("질문에 대한 답변을 생성 중입니다..."):
            context_docs = [retriever.contexts[retriever.notice_ids.index(nid)] for nid in notice_ids]
            joined_context = "\n\n".join(context_docs)
            full_prompt = f"""아래는 성균관대학교 공지사항 중 관련된 내용입니다:\n\n{joined_context}\n\n사용자의 질문: "{prompt}"\n\n위 공지를 참고하여 정리된 답변을 제공해주세요."""
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.5,
                )
                answer = response["choices"][0]["message"]["content"].strip()
            except Exception as e:
                answer = f"❗️OpenAI API 호출에 실패했습니다: {e}"
            st.write(answer)
            st.session_state["chat"].append(("assistant", answer))
