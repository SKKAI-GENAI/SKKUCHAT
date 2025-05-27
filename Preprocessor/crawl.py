import re
import json
import requests
from bs4 import BeautifulSoup as bs

from datetime import datetime
from zoneinfo import ZoneInfo


# 한 줄 패턴 
def extract_line_pattern(text, keywords):
    escaped_keywords = [re.escape(k) for k in keywords]
    keywords = '|'.join(escaped_keywords)
    line_pattern = rf"(?m)^\s*({keywords})[^:\n]*[:：)]\s*(.*)"
    match = re.search(line_pattern, text)
    if match:
        return match.group(2).strip()
    
    line_pattern2 = rf"(?m)^.*({keywords})[^:\n]*[:：)]\s*(.*)"
    match = re.search(line_pattern2, text)
    if match:
        return match.group(2).strip()
    
    return None


# 숫자 패턴
def extract_numbered_section(text, keywords):
    lines = text.splitlines()

    content = []
    collecting = False
    empty_count = 0

    for line in lines:
        number_match = re.match(r"^\s*(\d+)[).]\s*(.*)", line)
        if number_match:
            if collecting :
                return '\n'.join(content).strip()
            
            title = number_match.group(2)
            if any (kw in title for kw in keywords):
                content.append(title)
                collecting = True
        else:
            if collecting:
                if line == "":
                    empty_count+=1
                    if empty_count>1:
                        return '\n'.join(content).strip()
                empty_count = 0
                content.append(line)
    return None


# 문자 패턴
def extract_letter_section(text, keywords):
    lines = text.splitlines()

    content = []
    collecting = False
    empty_count = 0

    for line in lines:
        number_match = re.match(r"^\s*([가-힣])[).]\s*(.*)", line)
        if number_match:
            if collecting :
                return '\n'.join(content).strip()
            
            title = number_match.group(2)
            if any (kw in title for kw in keywords):
                content.append(title)
                collecting = True
        else:
            if collecting:
                if line == "":
                    empty_count+=1
                    if empty_count>1:
                        return '\n'.join(content).strip()
                empty_count = 0
                content.append(line)
    return None



# 기호 패턴 
def extract_symbol_section(text, keywords):
    lines = text.splitlines()

    collecting = False
    current_symbol = None
    content = []
    empty_count = 0

    for line in lines:
        symbol_match = re.match(r"^\s*([※◆■★◉●◎◇△▽▼▶◀\-○])\s*(.*)", line)
        if collecting:
            if symbol_match and symbol_match.group(1)==current_symbol:
                return ' '.join(content).strip()
            else:
                if line =="" :
                    empty_count+=1
                    if empty_count>=2:
                        return ' '.join(content).strip()
                    continue
                content.append(line)
        else:
            if symbol_match:
                symbol = symbol_match.group(1)
                title = symbol_match.group(2).strip()
                if any(kw in title for kw in keywords):
                    current_symbol = symbol
                    collecting = True
                    content.append(title)
            continue
    return None




# 공지 대상 추출
def extract_target(text):
    keywords = ['신청자격','신청 자격','자격요건','자격 요건','모집대상','모집 대상',
                '지원자격','지원 자격','공모대상','공모 대상','참가대상','참가 대상','신청대상','신청 대상',
                '대상 학생','대상학생','선발대상','채용 요건', '채용요건','지원대상','지원 대상',
                '선발 대상',]
    
    number_section_pattern = extract_numbered_section(text, keywords)
    if number_section_pattern!=None:
        return number_section_pattern
        
    letter_section_pattern = extract_letter_section(text, keywords)
    if letter_section_pattern != None:
        return letter_section_pattern
        
    symbol_section_pattern = extract_symbol_section(text, keywords)
    if symbol_section_pattern != None:
        return symbol_section_pattern
    
    line_pattern = extract_line_pattern(text, ['대상','자격'])
    if line_pattern != None:
        return line_pattern

    return ""


# 마감기한 추출 
def extract_due_date(text):
    keywords = ['신청 기간','신청기간','모집기간', '모집 기간','마감일','접수기간', '접수 기간',
                '신청마감일','신청 마감일','공모기간','공모 기간','참가접수','참가 접수','접수기한','접수 기한','제출 기한','제출기한',
                '참가신청','참가 신청','행사기간','행사 기간','학생신청',]
    
    number_section_pattern = extract_numbered_section(text, keywords)
    if number_section_pattern!=None:
        return number_section_pattern
        
    letter_section_pattern = extract_letter_section(text, keywords)
    if letter_section_pattern != None:
        return letter_section_pattern
        
    symbol_section_pattern = extract_symbol_section(text, keywords)
    if symbol_section_pattern != None:
        return symbol_section_pattern
    
    line_pattern = extract_line_pattern(text, keywords)
    if line_pattern != None:
        return line_pattern

    return ""


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

    for pg in range(3):
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
            target = extract_target(content)
            due = extract_due_date(content)

            data.append(
                {
                    "id": id,
                    "title": title,
                    "content": content,
                    "target": target,
                    "category": category,  # [채용/모집], [행사/세미나] 등
                    "due_date": due,
                    "created_date": created_date,  # 공지 작성일
                    "crawled_date": NOW_KST,  # 크롤링된 시간
                    "department": "홈페이지 공지사항",
                }
            )


    json_data = json.dumps(data, indent=4, ensure_ascii=False)

    with open("skku_notices.json", "w", encoding="utf-8") as f:
        f.write(json_data)
