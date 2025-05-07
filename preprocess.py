import re

def process(text):
    # 전처리 코드
    text = re.sub(r"[^a-zA-Z0-9가-힣\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokenized_text = text.split(" ")
    tokenized_text = " ".join([word for word in tokenized_text if word not in stop_words])
    token = tokenized_text.split(" ")
    return token

# content 항목 전처리
# from eunjeon import Mecab #pip install eunjeon 필요!
import pandas as pd

#불용어 사전
def load_stopwords():
    f=open("stopwords-ko.txt", "r", encoding="utf-8")
    stopwords_list = f.read().splitlines()
    return stopwords_list

stop_words=load_stopwords()

def Preprocess_text_content(text):
    mecab = Mecab()

    if pd.isnull(text):  # NaN 처리
        return ""

    # 특수문자 제거, 공백 정리, 불용어 제거 후 토큰화
    text = re.sub(r"[^a-zA-Z0-9가-힣\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokenized_text =mecab.morphs(text)
    tokenized_text = " ".join([word for word in tokenized_text if word not in stop_words])

    return tokenized_text