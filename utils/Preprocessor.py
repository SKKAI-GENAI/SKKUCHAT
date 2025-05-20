import re
import io
from PIL import Image

import pytesseract

# from eunjeon import Mecab
# mecab = Mecab()

with open("stopwords-ko.txt", "r", encoding="utf-8") as f:
    stopwords = f.read().splitlines()


def Preprocess_text(text):
    text = re.sub(r"[^a-zA-Z0-9가-힣\s]", " ", text) # 특수 문자 제거
    text = re.sub(r"\s+", " ", text).strip() # 공백 정리
    # tokenized_text = mecab.morphs(text)
    # tokenized_text = " ".join([word for word in tokenized_text if word not in stopwords])

    return text

def Preprocess_img(img_bytes):
    """
    이미지 바이트 데이터를 OCR에 적합하도록 전처리한 후, 텍스트를 추출합니다.

    Parameters:
        img_bytes (bytes): 이미지 파일의 바이트 데이터.

    Returns:
        str: 이미지에서 추출한 텍스트.
    """

    img = Image.open(io.BytesIO(img_bytes))

    MAX_WIDTH = 750
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)  # 이미지 축소, LANCZOS 필터 사용해 품질 유지

    img_text = pytesseract.image_to_string(img, lang="kor+eng", config="--oem 3 --psm 6")
    return img_text.strip()
