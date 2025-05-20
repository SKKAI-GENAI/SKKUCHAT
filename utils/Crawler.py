import re
import json
import requests

from datetime import datetime
from zoneinfo import ZoneInfo

from tqdm import tqdm
from bs4 import BeautifulSoup as bs

from Preprocessor import Preprocess_img


def Crawler(max_pages: int, img_OCR: bool = True):
    """
    성균관대학교 홈페이지 공지사항을 크롤링하여 JSON으로 저장합니다.

    Parameters:
        max_pages (int): 크롤링할 공지사항 페이지 수.
        img_OCR (bool, optional): 이미지 내 텍스트를 OCR로 추출할지 여부. 기본값은 True.

    Returns:
        None
    """

    NOW_KST = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
    URL = "https://www.skku.edu/skku/campus/skk_comm/notice01.do"

    query_list = lambda page: f"?mode=list&&articleLimit=10&article.offset={page*10}"
    query_view = lambda id: f"?mode=view&articleNo={id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Referer": "https://www.skku.edu/",
    }

    data = {}
    for page in tqdm(range(max_pages), desc="Crawling in progress"):
        # 공지사항 리스트 가져오기
        response = requests.get(URL + query_list(page), headers=headers)
        html = bs(response.text, "html.parser")

        headers["Referer"] = URL + query_list(page)

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

            # 공지사항 게시물 이미지 내 텍스트 추출(OCR)
            dd = subhtml.select_one("dd")
            image_tags = dd.select("img") if dd else []
            image_url = ["https://www.skku.edu/" + img["src"] for img in image_tags if img.has_attr("src")]
            image_url = image_url if image_url else None

            if (img_OCR and image_url is not None):
                for url in image_url:
                    if url.endswith((".jpg", ".jpeg", ".png", ".bmp")):
                        try:
                            img_response = requests.get(url, headers=headers)
                            img_text = Preprocess_img(img_response.content)
                            content += img_text
                        except Exception as e:
                            # 이미지 크기가 너무 큰 경우 Dos 공격 가능성 경고 메세지 발생
                            tqdm.write(f"OCR failed: {url} -> {e}")

            data[id] = {
                "id": id,
                "title": title,
                "content": content,
                "image_url": image_url,  # 이미지 URL
                "category": category,    # [채용/모집], [행사/세미나] 등
                "due_date": None,
                "created_date": created_date,  # 공지 작성일
                "crawled_date": NOW_KST,       # 크롤링된 시간
                "department": "홈페이지 공지사항",
            }

    # 크롤링 한 내용을 JSON으로 저장
    with open("skku_notices.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
