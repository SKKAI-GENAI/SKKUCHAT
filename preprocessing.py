import io
import warnings
from PIL import Image

import pytesseract

def Preprocess_img(img_bytes):
    """
    이미지 바이트 데이터를 OCR에 적합하도록 전처리한 후, 텍스트를 추출합니다.

    Parameters:
        img_bytes (bytes): 이미지 파일의 바이트 데이터.

    Returns:
        str: 이미지에서 추출한 텍스트.
    """
    # Dos 공격 가능성 경고 메세지(이미지 크기가 너무 클 때) 무시
    # 신뢰할 수 있는 출처(성균관대학교 홈페이지)에서 이미지를 받아오므로
    warnings.simplefilter("ignore", Image.DecompressionBombWarning)

    img = Image.open(io.BytesIO(img_bytes))

    MAX_WIDTH = 750
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)  # 이미지 축소, LANCZOS 필터 사용해 품질 유지

    img_text = pytesseract.image_to_string(img, lang="kor+eng", config="--oem 3 --psm 6")
    return img_text.strip()
