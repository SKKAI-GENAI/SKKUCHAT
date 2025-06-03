import streamlit as st

from dotenv import load_dotenv
from utils.Crawler import Crawler

from openai import OpenAI
from retrieval import SparseRetrieval

load_dotenv()

st.set_page_config(page_title="SKKUCHAT", page_icon="🤖")
st.title("🤖 SKKUCHAT(스꾸챗)")
st.subheader("ㅤㅤ성균관대 공지사항 챗봇")
st.write("")


@st.cache_resource(show_spinner="챗봇 로딩중...")
def load_retriever():
    Crawler(max_pages=100)
    retriever = SparseRetrieval()
    return retriever

retriever = load_retriever()

# 대화 기록
if "chat" not in st.session_state:
    st.session_state["chat"] = [
        (
            "assistant",
            "안녕하세요! 저는 성균관대학교 공지사항 챗봇, 스꾸챗입니다. 궁금한 점을 물어보세요!",
        ) # 첫 인삿말
    ]

# 기존 대화 기록 출력
for role, msg in st.session_state["chat"]:
    with st.chat_message(role):
        st.write(msg)

# 사용자 질문 입력
prompt = st.chat_input("성균관대 공지사항 관련 궁금한 점을 물어보세요!")

if prompt:
    # 대화 기록에 사용자 질문 추가
    st.chat_message("user").write(prompt)
    st.session_state["chat"].append(("user", prompt))

    # 관련 공지 검색
    with st.spinner("관련 공지사항 탐색 중..."):
        results = retriever.retrieve(prompt, topk=3)

    if not results:
        with st.chat_message("assistant"):
            st.write("❗️ 관련 공지를 찾지 못했어요. 아래와 같은 경우 공지사항을 제대로 찾을 수 없어요.")
            st.write("1. 입력된 질문이 비어있어요.")
            st.write("2. 질문이 너무 짧거나 명확하지 않아요.")
            st.write("3. 너무 포괄적인 질문이에요. 조금 더 자세하게 질문해주세요!")
            st.write("4. 성균관대학교 공지사항과 무관한 질문이에요.")
        st.session_state["chat"].append(("assistant", "❗️ 관련 공지를 찾지 못했어요. 아래와 같은 경우 공지사항을 제대로 찾을 수 없어요:\n1. 입력된 질문이 비어있어요.\n2. 질문이 너무 짧거나 명확하지 않아요.\n3. 너무 포괄적인 질문이에요. 조금 더 자세하게 질문해주세요!\n4. 성균관대학교 공지사항과 무관한 질문이에요."))
    else:
        notice_links = []
        for _, notice_info in results:
            title = notice_info["title"]
            url = f"https://www.skku.edu/skku/campus/skk_comm/notice01.do?mode=view&articleNo={notice_info["id"]}"
            notice_links.append((title, url))
        notice_text = "\n".join([f"{i+1}. {title} {url}" for i, (title, url) in enumerate(notice_links)])

        with st.chat_message("assistant"):
            st.write("🔎 관련 공지를 찾았어요:")
            st.write(notice_text)
            st.write([logit for logit, _ in results])
        st.session_state["chat"].append(("assistant", "🔎 관련 공지를 찾았어요:\n" + notice_text))

        # GPT 응답 생성
        with st.spinner("질문에 대한 답변 생성 중..."):
            context = [notice_info["content"] + "\n\n" for _, notice_info in results]
            full_prompt = f"""아래는 성균관대학교 공지사항 중 관련된 내용입니다:\n\n{context}\n\n사용자의 질문: "{prompt}"\n\n위 공지를 참고하여 정리된 답변을 제공해주세요."""

            try:
                client = OpenAI()
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=[{"role": "user", "content": full_prompt}],
                    temperature=0.5,
                )
                response = response.output_text
            except Exception as e:
                response = f"❗️OpenAI API 호출에 실패했습니다: {e}"

            st.chat_message("assistant").write(response)
            st.session_state["chat"].append(("assistant", response))
