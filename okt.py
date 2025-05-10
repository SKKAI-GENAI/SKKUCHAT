import pandas as pd
import re

# from eunjeon import Mecab    #pip install eunjeon 필요
from konlpy.tag import Okt


    
def load_stopwords():
    f=open("stopwords-ko.txt", "r", encoding="utf-8")
    stopwords_list = f.read().splitlines()
    return stopwords_list

stop_words=load_stopwords()


def tokenize_w_mecab(text):
    mecab = Mecab()
    tokenized_text = mecab.morphs(text)
    tokenized_text = " ".join([word for word in tokenized_text if word not in stop_words])
    return tokenized_text


def tokenize_w_okt(text):
    okt = Okt()
    tokenized_text = okt.morphs(text)
    tokenized_text = " ".join([word for word in tokenized_text if word not in stop_words])
    return tokenized_text


# 텍스트 전처리
# title 항목 전처리
def Preprocess_text_title(text):

    if pd.isnull(text):  # NaN 처리
        return ""

    # 특수문자 제거, 공백 정리, 불용어 제거 후 토큰화
    text = re.sub(r"[^a-zA-Z0-9가-힣\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    # tokenized_text = tokenize_w_mecab(text)
    tokenized_text = tokenize_w_okt(text)

    return tokenized_text



# content 항목 전처리
def Preprocess_text_content(text):

    if pd.isnull(text):  # NaN 처리
        return ""

    # 특수문자 제거, 공백 정리, 불용어 제거 후 토큰화
    text = re.sub(r"[^a-zA-Z0-9가-힣\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    # tokenized_text = tokenize_w_mecab(text)
    tokenized_text = tokenize_w_okt(text)

    return tokenized_text



# category 항목 전처리
def Preprocess_text_category(text):

    if pd.isnull(text):  # NaN 처리
        return ""

    # 특수문자 제거 및 공백 정리
    text = re.sub(r"[^a-zA-Z0-9가-힣\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    # tokenized_text = tokenize_w_mecab(text)
    tokenized_text = tokenize_w_okt(text)

    return tokenized_text



def apply_preprocess():
    df = pd.read_csv("skku_notices.csv")

    # 전처리 적용
    for col in ["title", "content", "category"]:
        if col in df.columns and col == "title":
            df[col] = df[col].apply(Preprocess_text_title)
        elif col in df.columns and col == "content":
            df[col] = df[col].apply(Preprocess_text_content)
        elif col in df.columns and col == "category":
            df[col] = df[col].apply(Preprocess_text_category)

    df.to_csv("Preprocessed_notices.csv", index=False, encoding='utf-8-sig')