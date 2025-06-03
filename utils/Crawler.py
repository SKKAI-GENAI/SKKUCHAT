import re
import json
import sqlite3
import requests

from datetime import datetime
from zoneinfo import ZoneInfo

from tqdm import tqdm
from bs4 import BeautifulSoup as bs

from utils.Preprocessor import Preprocess_text, Preprocess_img


def Crawler(max_pages: int, img_OCR: bool = True, save2DB: bool = True):
    """
    성균관대학교 홈페이지 공지사항을 크롤링하여 
    데이터베이스 혹은 JSON 파일에 저장합니다.

    Parameters:
        max_pages (int): 크롤링할 공지사항 페이지 수.
        img_OCR (bool, optional): 이미지 내 텍스트를 OCR로 추출할지 여부. 기본값은 True.
        save2DB (bool, optional): 크롤링된 데이터를 데이터베이스에 저장할지 여부. 기본값은 True.

    Returns:
        None
    """

    NOW_KST = lambda: datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
    URL = "https://www.skku.edu/skku/campus/skk_comm/notice01.do"

    query_list = lambda page: f"?mode=list&&articleLimit=10&article.offset={page*10}"
    query_view = lambda id: f"?mode=view&articleNo={id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Referer": "https://www.skku.edu/",
    }

    # 데이터베이스 연결 및 생성
    if save2DB:
        conn = sqlite3.connect("./data/notices.db")
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notices (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                due_date TEXT,
                created_date TEXT NOT NULL,
                crawled_date TEXT NOT NULL,
                department TEXT NOT NULL DEFAULT '홈페이지 공지사항',
                image_url TEXT
            )
        """
        )
        cur.execute('CREATE INDEX IF NOT EXISTS idx_notices_due_date ON notices(due_date)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_notices_crawled_date ON notices(crawled_date)')

        conn.commit()
    else:
        data = {}

    # 공지사항 크롤링
    crawl_active = True
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

            div = subhtml.select_one("div.fr-view")
            content += " ".join(p.get_text(strip=True) for p in div.find_all("p")) if div is not None else ""

            # 공지사항 게시물 이미지 내 텍스트 추출(OCR)
            dd = subhtml.select_one("dd")
            image_tags = dd.select("img") if dd else []
            image_url = ["https://www.skku.edu" + img["src"] for img in image_tags if img.has_attr("src")]
            image_url = image_url if image_url else None

            if (img_OCR and image_url is not None):
                for url in image_url:
                    if url.endswith((".jpg", ".jpeg", ".png", ".bmp")):
                        try:
                            img_response = requests.get(url, headers=headers)
                            img_text = Preprocess_img(img_response.content)
                            content += img_text + " "
                        except Exception as e:
                            tqdm.write(
                                f"[OCR Failed] Notice ID={id} | URL={url} -> Exception: {e}"
                            )

            # 텍스트 전처리
            # title = Preprocess_text(title) # 제목은 전처리 제외
            content = Preprocess_text(title + " " + content)

            # 데이터베이스에 데이터 삽입
            if save2DB:
                # 공지사항이 이미 존재하는지 확인
                cur.execute(
                    """
                    SELECT created_date
                    FROM notices
                    WHERE id = ?
                    """,
                    (int(id),),
                )
                row = cur.fetchone()

                if not row or created_date != row[0]:
                    cur.execute(
                        """
                        INSERT INTO notices (id, title, content, category, due_date, created_date, crawled_date, image_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            title = excluded.title,
                            content = excluded.content,
                            category = excluded.category,
                            due_date = excluded.due_date,
                            created_date = excluded.created_date,
                            crawled_date = excluded.crawled_date,
                            image_url = excluded.image_url
                        """,
                        (
                            int(id),
                            title,
                            content,
                            category,
                            None,
                            created_date,
                            NOW_KST(),
                            json.dumps(image_url),
                        ),
                    )

                    # 전체 데이터를 최대 maxpage * 10개까지만 유지하기 위해
                    # 오래된 데이터를 삭제
                    cur.execute(
                        """
                        DELETE FROM notices
                        WHERE id = (
                            SELECT id
                            FROM notices
                            WHERE (SELECT COUNT(*) FROM notices) >= ?
                            ORDER BY created_date ASC, id ASC
                            LIMIT 1
                        )
                        """,
                        (max_pages * 10,),
                    )
                    conn.commit()
                else:
                    crawl_active = False
                    break
            else:
                data[int(id)] = {
                    "title": title,
                    "content": content,
                    "category": category,  # [채용/모집], [행사/세미나] 등
                    "due_date": None,
                    "created_date": created_date,  # 공지 작성일
                    "crawled_date": NOW_KST(),       # 크롤링된 시간
                    "department": "홈페이지 공지사항",
                    "image_url": image_url,  # 이미지 URL
                }

        if not crawl_active:
            break

    if save2DB:
        conn.close()
    else:
        # 크롤링한 데이터를 JSON으로 저장
        with open("skku_notices.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
