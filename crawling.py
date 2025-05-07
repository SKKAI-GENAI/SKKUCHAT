import re
import json
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm

from datetime import datetime
from zoneinfo import ZoneInfo

def crawl_skku_notice():
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

    print("crawling skku notice page...")
    for pg in tqdm(range(10)):
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

            data.append(
                {
                    "id": id,
                    "title": title,
                    "content": content,
                    "category": category,  # [채용/모집], [행사/세미나] 등
                    "created_date": created_date,  # 공지 작성일
                    "crawled_date": NOW_KST,  # 크롤링된 시간
                    "department": "홈페이지 공지사항",
                }
            )


    json_data = json.dumps(data, indent=4, ensure_ascii=False)

    with open("skku_notices.json", "w", encoding="utf-8") as f:
        f.write(json_data)

def get_data():
    with open('skku_notices.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        print('data error: first run run.py as prepare mode')
        exit(1)

    return data