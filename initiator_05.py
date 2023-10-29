import os, csv
import subprocess
import time
import shutil
import psutil
import pandas as pd
import configparser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from selenium import webdriver
import pandas as pd
import traceback
import tkinter as tk
import threading
import ctypes
from tkinter import Entry, Label, Button, Text, Scrollbar, END
from queue import Queue, Empty  # Empty를 직접 import 해야 합니다.
import queue





def is_admin2():
    try:
        # 관리자 권한으로 실행되고 있는지 확인합니다.
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
def copy_folder():
    source = "C:\\Program Files (x86)\\Google"
    destination = "C:\\Program Files\\Google"

    if not os.path.exists(source):
        # 소스 디렉토리가 존재하지 않으면 아무 것도 하지 않고 종료
        return

    if os.path.exists(destination):
        
        # 목적지 디렉토리가 이미 존재하면 아무 것도 하지 않고 종료
        return

    # 디렉토리 복사 (하위 디렉토리 및 파일 포함)
    if is_admin():
        shutil.copytree(source, destination)

blog_name = ""
blog_url = ""
browser_position =""
exe_file="./dist/BlogReply_extractor09.exe"


# GUI 창 생성 및 구성
root = tk.Tk()
root.title("블로그 정보 입력")

tk.Label(root, text="블로그 이름").grid(row=0, padx=20, pady=5)
tk.Label(root, text="블로그 URL").grid(row=1, padx=20, pady=5)

blog_name_entry = tk.Entry(root, width = 30)
blog_name_entry.grid(row=0, column=1, padx=20, pady=5)

blog_url_entry = tk.Entry(root, width = 30)
blog_url_entry.grid(row=1, column=1, padx=20, pady=5)

# 로그 출력을 위한 Text 위젯과 Scrollbar 추가
log_text = Text(root, wrap="word", width=50, height=10)
log_text.grid(row=4, column=0, columnspan=2, sticky="nsew")
scrollbar = Scrollbar(root, command=log_text.yview)
scrollbar.grid(row=4, column=2, sticky="ns")
log_text.config(yscrollcommand=scrollbar.set)




# 로그 메시지를 GUI에 출력하는 함수
def log(message):
    def _log():
        log_text.insert(END, message + "\n")
        log_text.yview(END)
    
    root.after(0, _log)  # 메인 스레드에서 _log 함수 실행
    
    
main_links_info=[]
def run_exe_if_required():
    blog_name = blog_name_entry.get()
    blog_url = blog_url_entry.get()
    blog_entries = [(blog_name, blog_url)]
    for blog_name, blog_url in blog_entries:
        
        try:
            if not os.path.exists(results_base_dir) or not os.path.exists(mid_files_dir):
                # subprocess.call([exe_file])
                threaded_start_extractor()
                # while_remain_post()
                
            elif os.path.exists(last_i_value_filename) and os.path.exists(PostList_file):
                if os.path.exists(exe_file):
                    while_remain_post()
            
            else:
                shutil.rmtree(results_base_dir)
                log(f"{blog_name} 폴더를 삭제했습니다. 프로그램을 재실행해 주세요")
                input("Press Enter to continue...")
                
        except Exception as e:
            log(f"def run_exe_if_required: {e}")
            log(traceback.format_exc()) 
            
            
def is_exe_running(exe_file):
    for process in psutil.process_iter():
        try:
            if exe_file.lower() == process.exe().lower():
                return True
        except Exception as e:
            log(f"is_exe_running: {e}")
            log(traceback.format_exc())
            log("\n봇방지로 인해 프로그램이 종료되었습니다..")
    return False

def restart_exe(exe_file):
    if not is_exe_running(exe_file):
        log('DB 추출 실행 파일을 재시작합니다.')
        threaded_start_extractor()

def remove_duplicate():
    # 중복 데이터 제거
    data = pd.read_csv(output_csv)
    data_no_duplicates = data.drop_duplicates()

    # 최종DB.csv로 저장
    data_no_duplicates.to_csv(final_csv, index=False)

    # output.csv 파일을 다른 폴더로 이동
    if not os.path.exists(mid_files_dir):
        os.mkdir(mid_files_dir)
    shutil.move(output_csv, f'{mid_files_dir}/{blog_name}_output.csv')
    log(f"{final_csv} 파일에 추출이 완료되었습니다.")
    FLAG01 = True
    input("Press Enter to continue...")
    
def while_remain_post():
    with open(PostList_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            link, has_like, has_comment = line.strip().split(',')
            main_links_info.append((link, has_like == 'True', has_comment == 'True'))
        
    with open(last_i_value_filename, 'r') as f:
        last_i = int(f.read().strip())
    
    while last_i < len(main_links_info):
        link, has_like, has_comment = main_links_info[last_i]
        has_like = has_like == True
        has_comment = has_comment == True
                
        # 그외에는 이전과 동일한 프로세스를 수행합니다.
        with open(last_i_value_filename, 'r') as f:
            last_i = int(f.read().strip())
        threaded_start_extractor()

        
        while True:
            time.sleep(3)
            restart_exe(exe_file)
            break
    else:
        remove_duplicate()

FLAG_Submit = False  
def submit_action():
    global blog_name
    global blog_url
    blog_entries = [(blog_name, blog_url)]
    blog_name = blog_name_entry.get()
    blog_url = blog_url_entry.get()
    

    # GUI의 현재 위치와 크기를 가져옵니다.
    gui_x = root.winfo_rootx()
    gui_y = root.winfo_rooty()
    gui_width = root.winfo_width()
    # gui_height = root.winfo_height()
    
    # 창의 위치 정보를 전역 변수에 저장합니다.
    global browser_position
    browser_position = (gui_x + gui_width, gui_y)  # 창 사이의 작은 간격을 위해 10을 추가합니다.
    save_and_initiate()
    
    # start_extractor를 스레드에서 실행합니다.
    # thread = threading.Thread(target=start_extractor,args=(exe_file, log_text, browser_position))
    # thread.start()

def save_and_initiate():
    filename = './_SetFiles/blog_list.csv'
    with open(filename, 'w', newline='', encoding='cp949') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['blog_name', 'blog_url'])
        writer.writerow([blog_name, blog_url])

    run_exe_if_required()
    
    
def check_log_queue():
    try:
        while True:
            text = log_queue.get_nowait()  # 큐에서 로그 메시지를 가져옵니다.
            # 실제 로그 출력 처리 (예: 텍스트 위젯에 메시지 출력)
            log_text.insert("end", text)  # 'log_text'는 로그 메시지를 표시하는 Tkinter 위젯일 수 있습니다.
    except queue.Empty:
        # 큐가 비어 있으면 아무 것도 하지 않습니다.
        pass

    # 큐를 계속 확인합니다.
    root.after(100, check_log_queue)  # 'root'는 Tkinter의 메인 창 인스턴스입니다.


# 로그 메시지를 저장할 큐 생성
log_queue = queue.Queue()
def start_extractor(exe_file, log_text, browser_position):
    # global browser_position
    x, y = browser_position

    def read_stream(stream, callback):
        while True:
            line = stream.readline()  # 스트림에서 한 줄씩 읽기
            if line:  # line이 빈 문자열이면 EOF(파일의 끝)을 의미합니다.
                callback(line)
            else:
                break  # EOF에 도달하면 반복을 종료합니다.

    def stream_output(process):
        def enqueue_output(line):
            log_queue.put(line)  # 큐에 로그 메시지를 추가합니다.
        # 표준 출력과 표준 에러를 각각 다른 스레드로부터 읽어옵니다.
        stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, enqueue_output))
        stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, enqueue_output))

        stdout_thread.start()
        stderr_thread.start()

        stdout_thread.join()  # 스레드가 종료될 때까지 기다립니다.
        stderr_thread.join()

        process.stdout.close()  # 스트림을 닫습니다.
        process.stderr.close()
        process.wait()  # 프로세스가 종료될 때까지 기다립니다.

    # subprocess.Popen으로 외부 프로세스를 시작합니다.
    process = subprocess.Popen(
        [exe_file, "--x-pos", str(x), "--y-pos", str(y)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True,  # text 모드로 설정, universal_newlines=True와 같습니다.
        bufsize=1,  # 줄 단위로 버퍼링
    )
    check_log_queue()
    # 출력을 처리할 스레드를 생성하고 시작합니다.
    output_thread = threading.Thread(target=stream_output, args=(process,))
    output_thread.start()

def threaded_start_extractor():
    # 'exe_file', 'log_text', 'browser_position'을 인자로 추가해야 합니다.
    extractor_thread = threading.Thread(target=start_extractor, args=(exe_file, log_text, browser_position))
    extractor_thread.start()
# 스레드를 시작합니다.



submit_button = tk.Button(root, text="제출", command=submit_action)
submit_button.grid(row=2, column=1, pady=20)

gui_width = root.winfo_width()
gui_x = root.winfo_x()
gui_y = root.winfo_y()

# 파일 및 디렉터리 경로 생성
base_dir = '.'  # 기본 디렉터리 설정
results_base_dir = os.path.join(base_dir, '결과파일', blog_name_entry.get())
mid_files_dir = os.path.join(results_base_dir, 'MidFiles')

# 파일 경로 설정
timesleep_file = os.path.join(base_dir, '_SetFiles', '인터넷속도.txt')
output_csv = os.path.join(results_base_dir, f'{blog_name_entry.get()}_output.csv')
final_csv = os.path.join(results_base_dir, f'{blog_name_entry.get()}_최종DB.csv')
last_i_value_filename = os.path.join(mid_files_dir, f'{blog_name_entry.get()}_last_value.txt')
PostList_file = os.path.join(mid_files_dir, f'{blog_name_entry.get()}_PostList.txt')

root.mainloop()


