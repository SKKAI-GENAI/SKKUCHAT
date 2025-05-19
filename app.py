import streamlit as st

if "chat" not in st.session_state:
    st.session_state["chat"] = []

with st.chat_message("assistant"):
    st.write("안녕하세요, 저는 스꾸챗입니다!")

for role, message in st.session_state["chat"]:
    with st.chat_message(role):
        st.write(message)

prompt = st.chat_input("성균관대학교에 대해 궁금한 점을 질문해주세요")
if prompt:
    st.session_state["chat"].append(("user", prompt))
    ## BM25 결과를 append
    # st.session_state["chat"].append(("assistant", result))
    st.rerun()
