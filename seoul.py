import httpx
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import os

# 페이지별 html, 게시글 링크 가져오기
def collect_post_urls(page_number:int):
    base_url = 'https://news.seoul.go.kr/culture/archives/category/art-news_c1/culture-and-arts-business_c1/news_art-news-n1'
    
    if page_number == 1:
        url = base_url
    elif page_number > 1:
        url = f"{base_url}/page/{page_number}"
    
    with httpx.Client() as client:
        response = client.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        posts = [post.get('href') for post in soup.select('.post-lst .tit a')]        
        
        return posts
    
posts_urls = collect_post_urls(3)
print(posts_urls) # 해당 페이지에 있는 게시글 들(10개)

# 본문에 있는 링크/첨부파일/이미지 수집
def extract_attached_file(post_url):

    with httpx.Client() as client:
        response = client.get(post_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # 메타데이터 만들기 - 저장 정보(게시글, 담당부서, 문의, 수정일)
        meta_raw = soup.select_one('#view_top')
        title = meta_raw.select_one('h3').get_text(strip=True)

        # 담당부서 (class="dept"인 <dd> 태그)
        department = meta_raw.find('dd', class_='dept')
        department_text = '-'.join(span.get_text(strip=True) for span in department.find_all('span')) if department else ''

        # 문의 전화번호 (담당부서 <dd> 다음 <dd>)
        telephone = department.find_next_sibling('dd')
        telephone_text = telephone.get_text(strip=True) if telephone else ''

        # 수정일 (문의 전화번호 <dd> 다음 <dd>)
        postdate = telephone.find_next_sibling('dd') if telephone else None
        postdate_text = postdate.get_text(strip=True) if postdate else ''

        # 최종 출력
        output = f"제목:{title}, 담당부서: {department_text}, 문의: {telephone_text}, 수정일:{postdate_text}"
        print(output)

        # 저장이 필요한 첨부파일 형식 (해시로 저장해야 검색속도가 빠르다 - if문으로 해당 데이터 내에 있는 확장자인지 확인할 때)
        file_form = {'.pdf', 'image/jpeg', 'image/png', '.hwp', '.hwpx', '.xlsx', '.ppt', '.pptx', '.doc', '.docx', '.jpg', '.png', '.csv', '.txt'}

        # 링크/첨부파일/이미지 수집
        attached_files = [tag.get('href') or tag.get('src') for tag in soup.select('#container_area a, #container_area img')]

        # 정규식으로 빠르게 확장자 추출
        def get_extension(url):
            match = re.search(r'\.([a-zA-Z0-9]+)$', urlparse(url).path)  # 확장자 추출
            return f".{match.group(1).lower()}" if match else ""  # 확장자 소문자로 변환
                
        # 벡터화 처리 → map()으로 빠르게 확장자 추출
        extensions = list(map(get_extension, attached_files))

        # 파일과 일반 링크 분류
        file_links = [link for link, ext in zip(attached_files, extensions) if ext in file_form]
        normal_links = [link for link, ext in zip(attached_files, extensions) if ext not in file_form]

        return {
            "meta-data": output,
            "attached_files": file_links,
            "extra_links": normal_links
            }


attached_files = extract_attached_file(posts_urls[1])
print(attached_files)

def convert_to_https(url):
    """ //로 시작하는 URL을 https://로 변환 """
    return "https:" + url if url.startswith("//") else url

def download_file(url, save_dir="downloads"):
    """ 주어진 URL의 파일 다운로드하고 저장 """
    url = convert_to_https(url)  # https 변환
    filename = os.path.join(save_dir, os.path.basename(url))

    try:
        with httpx.Client() as client:
            response = client.get(url, follow_redirects=True)
            if response.status_code == 200:
                os.makedirs(save_dir, exist_ok=True)
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"파일 저장 완료: {filename}")
                return filename
            else:
                print(f"다운로드 실패: {url} (HTTP {response.status_code})")
    except Exception as e:
        print(f"오류 발생: {url}, 오류: {e}")

    return None

def download_all_files(urls):
    """ 모든 파일 다운로드 """
    saved_files = [download_file(url) for url in urls]
    return saved_files

saved_files = download_all_files(attached_files.get("attached_files"))