from selenium import webdriver
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from os import path
import os, random, re, sys
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import argparse
import requests
from tkinter import messagebox

parser = argparse.ArgumentParser(description="블로그 추출기를 사용자 정의된 브라우저 위치 및 크기로 실행합니다.")
parser.add_argument('--x-pos', type=int, help="브라우저 창의 X 위치")
parser.add_argument('--y-pos', type=int, help="브라우저 창의 Y 위치")
parser.add_argument('--width', type=int, help="브라우저 창의 너비")
parser.add_argument('--height', type=int, help="브라우저 창의 높이")

args = parser.parse_args()

 # Wait and Scroll Logic
def ScrollDowntoEnd(wait_class, direction):
    print('스크롤 중...')
    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        if direction == 'down':
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(sleeptime)
        if direction == 'up': 
            driver.execute_script("window.scrollBy(0, -30000);")
            time.sleep(sleeptime)
        try:
            WebDriverWait(driver, 8 + sleeptime).until(EC.presence_of_element_located((By.CLASS_NAME, wait_class)))
        except:
            time.sleep(sleeptime)
            pass
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

# LoadHTML(driver)
def LoadHTML(driver):
    html = driver.page_source
    time.sleep(sleeptime)
    soup = BeautifulSoup(html, 'html.parser')
    return soup

# 사용자의 user_agent를 저장하는 파일 경로 설정
USER_AGENT_FILE_PATH = './_SetFiles/라이선스.txt'

def get_saved_user_agent():
    """
    저장된 user_agent를 반환합니다. 파일이 없으면 None을 반환합니다.
    """
    if os.path.exists(USER_AGENT_FILE_PATH):
        with open(USER_AGENT_FILE_PATH, 'r') as file:
            return file.read().strip()
    else:
        return None

def save_user_agent(user_agent):
    """
    주어진 user_agent를 파일에 저장합니다.
    """
    with open(USER_AGENT_FILE_PATH, 'w') as file:
        file.write(user_agent)
        
# Selenium 설정
def Sel_set_driver():
    chromedriver_autoinstaller.install()
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # 사용자 정의 창 위치 및 크기 인수가 제공된 경우 적용합니다.
    if args.x_pos is not None and args.y_pos is not None:
        options.add_argument(f"--window-position={args.x_pos},{args.y_pos}")
    if args.width is not None and args.height is not None:
        options.add_argument(f"--window-size={args.width},{args.height}")
    # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    # options.add_argument('user-agent=' + user_agent)
    
    # 사용자의 실제 user_agent를 가져옵니다.
    user_agent = webdriver.Chrome(options=options)

   
    
    # if not os.path.exists(USER_AGENT_FILE_PATH):
    #     os.makedirs(USER_AGENT_FILE_PATH, exist_ok=True)
    #     save_user_agent(user_agent)
        
    
    # saved_user_agent = get_saved_user_agent()

    # # 이전에 user_agent가 저장되어 있고, 현재의 user_agent와 다르다면,
    # if saved_user_agent and saved_user_agent != user_agent:
    #     messagebox.showerror(
    #         "Error", "PC가 변경되었습니다. 새 라이선스가 필요합니다. 크롤링 크루에 문의하세요."
    #     )
    #     sys.exit("프로그램을 종료합니다.")  # 프로그램을 종료합니다.

    # # 처음 실행이거나 user_agent가 같다면, 현재 user_agent를 저장합니다.
    # if not saved_user_agent:
    #     save_user_agent(user_agent)
    #     messagebox.showerror(
    #         "라이선스 등록 알림",
    #         "사용하고 계신 PC가 등록되었습니다. 다른 PC에서는 사용이 제한됩니다."
    #     )
    # time.sleep(2)
    # options.add_argument(f'user-agent={user_agent}')
    
    
    
    #크롬창 정보
    # if args.x_pos is not None and args.y_pos is not None:
    #     options.add_argument(f"--window-position={args.x_pos},{args.y_pos}")
    # else: pass
    driver = webdriver.Chrome(options=options)
    return driver

# 인터넷속도 = time sleep 속도 읽어오기
timesleep_file = f'./_SetFiles/인터넷속도.txt'
if os.path.exists(timesleep_file):
    with open(timesleep_file, 'r') as f:
        sleeptime = int(f.read().strip())
else: 
    with open(timesleep_file, 'w') as f:
        f.write(2)
        
# Load base URLs and blog names from CSV
with open('./_SetFiles/blog_list.csv', 'r', encoding='cp949') as file:
    reader = csv.reader(file)
    next(reader)  # 헤더 건너뛰기
    blog_entries = []
    for row in reader:
        blog_entries.append((row[0], row[1]))

for blog_name, blog_url in blog_entries:
    # print(blog_url)
    blog_ID = blog_url.split('blog.naver.com/')[1].split('/')[0]
    m_blog_url = f"https://m.blog.naver.com/{blog_ID}"
    pc_blog_url = f"https://blog.naver.com/{blog_ID}"
    base_url = f"https://m.blog.naver.com/PostList.naver?blogId={blog_ID}&categoryNo=0&from=postList&listStyle=post"
    driver = Sel_set_driver()
    #Target Directory 생성
    TargetDir01 = f'./결과파일/{blog_name}/MidFiles'
    if os.path.exists(TargetDir01)==False:
        os.makedirs(TargetDir01, exist_ok=True)
    else: pass
        
    # 전체 포스트 링크 및 댓글/공감 유무 추출
    PostList_file = f'{TargetDir01}/{blog_name}_PostList.txt'
    IsFile = os.path.exists(PostList_file)
    main_links_info = []  # This will store tuples of (link, has_like, has_comment)
    if IsFile == False:
        sleeptime = 3
        driver.switch_to.window(driver.window_handles[0])
        driver.get(base_url)
        time.sleep(sleeptime)
        ScrollDowntoEnd('link__OVpnJ', 'down')
        soup = LoadHTML(driver)
        
        postlist_div = soup.find('div', class_='list__fJdGM')
        
        for post in postlist_div.find_all('div', class_='postlist__LXY3R'):
            link = post.find('a', class_='link__OVpnJ')
            if link:
                has_like = bool(post.find('span', class_='like____2o5'))
                has_comment = bool(post.find('span', class_='comment___IpyZ'))
                main_links_info.append((link['href'], has_like, has_comment))
        
        print('추출된 글개수: ',len(main_links_info))

        # Saving the main_links_info to PostList_file
        with open(PostList_file, 'w', newline='\n') as f:
            for link_info in main_links_info:
                f.write(','.join(map(str, link_info)) + '\n')
                
    else:
        with open(PostList_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                link, has_like, has_comment = line.strip().split(',')
                main_links_info.append((link, has_like == 'True', has_comment == 'True'))
        print('추출된 글개수: ',len(main_links_info))

                
            
    # 인터넷속도 = time sleep 속도 다시 읽어오기
    with open(timesleep_file, 'r') as f:
        sleeptime = int(f.read().strip())        
      

    last_i_value_filename = f'{TargetDir01}/{blog_name}_last_ivalue.txt'
    if os.path.exists(last_i_value_filename):
        with open(last_i_value_filename, 'r') as f:
            start_i = int(f.read().strip())
    else:
        start_i = 0
    
    전체포스트갯수 = len(main_links_info)
    all_ids = set()
    i = start_i
    FLAG1 = False
    for link, has_like, has_comment in main_links_info[start_i:]:
        link = link
        has_like = has_like == True
        has_comment = has_comment == True
        
        try:
            # print('link', link)
            post_id_mid = link.replace(f'https://m.blog.naver.com/{blog_ID}/','')
            post_id = post_id_mid.replace('?referrerCode=1','')
            # print('\npost_id', post_id)
            

            # Extract IDs from like_more_link 공감
            if has_like:
                print(f"\n공감 DB 추출 중.. 전체 {전체포스트갯수}개 글 중 {i+1}번째 글")
                current_ids_like = set()
                like_more_link = f'https://m.blog.naver.com/SympathyHistoryList.naver?blogId={blog_ID}&logNo={post_id}&categoryId=POST'
                # print('like_more_link_sleeptime:', sleeptime)
                driver.get(like_more_link)
                time.sleep(1)
                try:
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'num___9TRf')))
                except:pass
                total_num = int(driver.find_element(By.CLASS_NAME, 'num___9TRf').text.replace(',',''))
                # print(f"공감 DB의 총 갯수는 {total_num}개 입니다.")
                ScrollDowntoEnd('link__D9GoZ', 'down')
                soup = LoadHTML(driver)
                try:
                    # bloger_area___eCA_ 아래의 link__D9GoZ 클래스를 가진 모든 a tag를 수집합니다.
                    for a_tag in soup.select('div.bloger_area___eCA_ a.link__D9GoZ'):
                        extracted_id = a_tag['href'].replace('https://m.blog.naver.com/', '')
                        current_ids_like.add(extracted_id)
                    all_ids.update(current_ids_like)
                except: pass
                print(f"{i+1}번째 글의 공감에서 {len(current_ids_like)}개의 ID를 추출했습니다.")
            else:
                print(f"\n전체 {전체포스트갯수}개 글 중 {i+1}번째 글은 공감을 허용하지 않는 포스트입니다.")
                
            # Extract IDs from reply_link 댓글
            if has_comment:
                print(f"\n댓글 DB 추출 중.. 전체 {전체포스트갯수}개 글 중 {i+1}번째 글")
                current_ids_reply = set()
                reply_link = f'https://m.blog.naver.com/CommentList.naver?blogId={blog_ID}&logNo={post_id}'
                # print('reply_link', reply_link)
                driver.get(reply_link)
                time.sleep(1)
                try:
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'num___9TRf')))
                except: pass
                total_num = int(driver.find_element(By.CLASS_NAME, 'num___9TRf').text.replace(',',''))
                # print(f"댓글의 총 갯수는 {total_num}개 입니다.")
                ScrollDowntoEnd('u_cbox_name', 'up')
                soup = LoadHTML(driver)
                try:
                    for a_tag in soup.find_all('a', class_='u_cbox_name'):
                        current_ids = a_tag['href'].replace('https://m.blog.naver.com/PostList.naver?blogId=', '')
                        current_ids_reply.add(current_ids)
                    all_ids.update(current_ids_reply)
                except: pass
                print(f"{i+1}번째 글의 댓글에서 {len(current_ids_reply)}개의 ID를 추출했습니다.")
            else:
                print(f"\n전체 {전체포스트갯수}개 글 중 {i+1}번째 글은 댓글을 허용하지 않는 포스트입니다.")
            
            output_filename = f"./결과파일/{blog_name}/{blog_name}_output.csv"
            with open(output_filename, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # writer.writerow(["Email"])
                for id in all_ids:
                    writer.writerow([id + "@naver.com"])
            all_ids.clear()
            i = i + 1
            with open(last_i_value_filename, 'w') as f:
                f.write(str(i))
                
        except:
            FLAG1 = True 
            # driver.quit()
            break
        
    if FLAG1 == True:
        # FLAG2 = True
        break

# Close the browser
driver.quit()
