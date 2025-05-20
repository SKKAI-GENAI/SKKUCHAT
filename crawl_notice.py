import re
import json
import requests
import os

from tqdm import tqdm
from bs4 import BeautifulSoup as bs

from datetime import datetime
from zoneinfo import ZoneInfo

from preprocessing import Preprocess_img

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

# Load existing JSON data
if os.path.exists("skku_notices.json"):
    with open("skku_notices.json", "r", encoding="utf-8") as f:
        existing_data = json.load(f)
else:
    existing_data = []

existing_ids = {item["id"] for item in existing_data}
updated_count = 0
flag = 0

for pg in tqdm(range(100)):
    # 공지사항 리스트 가져오기
    if flag == 1:
        break
    response = requests.get(URL + query_list(pg), headers=headers)
    html = bs(response.text, "html.parser")

    headers["Referer"] = URL + query_list(pg)

    notice_list = html.select("dl.board-list-content-wrap ")
    for notice in notice_list:
        category = notice.select_one("span.c-board-list-category").get_text(strip=True)

        url = notice.select_one("a")["href"]
        id = re.search(r"articleNo=(\d+)", url).group(1)
        title = notice.select_one("a").get_text(strip=True)

        if id in existing_ids:
            tqdm.write(f"[Update Stopped] Notice ID={id} already exists.")
            flag = 1
            break

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
        image_url = ["https://www.skku.edu" + img["src"] for img in image_tags if img.has_attr("src")]
        image_url = image_url if image_url else None

        if (image_url is not None):
            for url in image_url:
                if url.endswith((".jpg", ".jpeg", ".png", ".bmp")):
                    try:
                        img_response = requests.get(url, headers=headers)
                        img_text = Preprocess_img(img_response.content)
                        content += img_text
                    except Exception as e:
                        tqdm.write(
                            f"[OCR Failed] Notice ID={id} | URL={url} -> Exception: {e}"
                        )

        data.append(
            {
                "id": id,
                "title": title,
                "content": content,
                "image_url": image_url,  # 이미지 URL
                "category": category,  # [채용/모집], [행사/세미나] 등
                "created_date": created_date,  # 공지 작성일
                "crawled_date": NOW_KST,  # 크롤링된 시간
                "department": "홈페이지 공지사항",
            }
        )
        updated_count += 1

    if updated_count > 0:
        tqdm.write(f"[Update Completed] {updated_count} new notices added.")
        break

# Merge new data with existing data
merged_data = data + existing_data
if len(data) > 0:
    # Remove the oldest notices if the total exceeds the limit
    merged_data = sorted(merged_data, key=lambda x: x["created_date"], reverse=True)
    if len(merged_data) > len(existing_data):
        merged_data = merged_data[:len(existing_data)]

# Save updated JSON data
with open("skku_notices.json", "w", encoding="utf-8") as f:
    json.dump(merged_data, f, indent=4, ensure_ascii=False)
