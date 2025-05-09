import re
import json
import requests
import csv
import pytesseract  #pip install pytesseract 필요
import io
import requests

from urllib.parse import urljoin    #5/9 이미지 추출 위함
from PIL import Image   #pip install pillow 필요
from bs4 import BeautifulSoup as bs

from datetime import datetime
from zoneinfo import ZoneInfo

def preprocess_image_for_ocr(img_bytes):
    img = Image.open(io.BytesIO(img_bytes))

    # 이미지 크기 확인
    max_width = 2000
    max_height = 3000

    if img.width > max_width or img.height > max_height:
        ratio = min(max_width / img.width, max_height / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)  #이미지 축소

    return img

def crawl_skku_notices():
    NOW_KST = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
    URL = "https://www.skku.edu/skku/campus/skk_comm/notice01.do"
    query_list = lambda pg: f"?mode=list&&articleLimit=10&article.offset={pg*10}"
    query_view = lambda id: f"?mode=view&articleNo={id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Referer": "https://www.skku.edu/",
    }

    data = []

    for pg in range(10):
        # 공지사항 리스트 가져오기
        response = requests.get(URL + query_list(pg), headers=headers)
        html = bs(response.text, "html.parser")

        headers["Referer"] = URL + query_list(pg)

        notice_list = html.select("dl.board-list-content-wrap ")
        for notice in notice_list:
            category = notice.select_one("span.c-board-list-category").get_text(strip=True)

            url = notice.select_one("a")["href"]
            id = re.search(r"articleNo=(\d+)", url).group(1)
            title = notice.select_one("a").get_text(strip=True)

            info = notice.select_one("dd.board-list-content-info")
            created_date = info.select("ul li")[2].get_text(strip=True)

            # 공지사항 게시물 가져오기
            subresponse = requests.get(URL + query_view(id), headers=headers)
            subhtml = bs(subresponse.text, "html.parser")

            pre = subhtml.select_one("pre.pre")
            content = pre.get_text(strip=True) if pre is not None else ""

            # 공지사항 게시물 이미지 내 텍스트 추출
            dd = subhtml.select_one("dd")
            image_tags = dd.select("img") if dd else []
            image_url = [urljoin(URL, img["src"]) for img in image_tags if img.has_attr("src")]
            image_url = image_url if image_url else None

            img_text = ""

            if image_url is not None:
                for url in image_url:
                    try:
                        if url.endswith((".jpg", ".jpeg", ".png", ".bmp")):
                            # 이미지 전처리 후 OCR
                            img_response = requests.get(url, headers=headers)
                            img = preprocess_image_for_ocr(img_response.content)
                            text = pytesseract.image_to_string(img, lang="kor", config="--oem 3 --psm 6")
                            img_text += text.strip()
                            """
                            # 이미지 OCR
                            img_response = requests.get(url, headers=headers)
                            img = Image.open(io.BytesIO(img_response.content))
                            text = pytesseract.image_to_string(img, lang="kor")
                            img_text += text.strip()
                            """
                        else:
                            continue
                    except Exception as e:
                        print(f"OCR 실패: {url} → {e}")
            # 기존 content에 이미지에서 추출한 텍스트 덧붙이기
            content = content + img_text
        
            data.append(
                {
                    "id": id,
                    "title": title,
                    "content": content,
                    "category": category,  # [채용/모집], [행사/세미나] 등
                    "created_date": created_date,  # 공지 작성일
                    "crawled_date": NOW_KST,  # 크롤링된 시간
                    "department": "홈페이지 공지사항",
                    "image_url":image_url # 이미지 URL
                }
            )


    json_data = json.dumps(data, indent=4, ensure_ascii=False)

    # 크롤링 한 내용을 JSON으로 저장
    with open("skku_notices.json", "w", encoding="utf-8") as f:
        f.write(json_data)

    # JSON을 CSV로 변환
    with open("skku_notices.json",'r',encoding='utf-8') as input_file, open("skku_notices.csv", 'w', newline='', encoding='utf-8') as output_file:
        data=json.load(input_file)
        f=csv.writer(output_file)

        f.writerow(["id", "title", "content", "category", "created_date", "crawled_date", "department"])  # Write the header row
        
        for row in data:
            f.writerow([row["id"], row["title"], row["content"], row["category"], row["created_date"], row["crawled_date"], row["department"]])