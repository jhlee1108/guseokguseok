#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modules for CGI handling
import cgi, cgitb
cgitb.enable()
import sqlite3 # 데이터베이스 접근
import time # unix_time 시간 변환
import sys # 종료
import configparser # 설정파일 읽기


def _fail_response(user_id):
    """불러오기 실패 응답
    """
    print("<html>")
    print("<head>")
    print("  <title>DNLab 출석부</title>")
    print("</head>")
    print("<body>")
    print("  <h1>정보 확인 실패</h1>")
    print("  <h2>등록되지 않은 학번이거나 학번을 잘못입력했습니다.</h2>")
    print("  <h3>{0}</h3>".format(user_id))
    print("  <a href='/index.html'> Return to mainpage </a>")
    print("</body>")
    print("</html>")


def _success_response(user_id, log_set):
    """불러오기 성공 응답
    """
    print("<html>")
    print("<head>")
    print("  <title>DNLab 출석부</title>")
    print("</head>")
    print("<body>")
    print("  <h1>정보 확인 성공</h1>")
    print("  <h2>안녕하세요. {0}</h2>".format(user_id))
    print("  <p>")
    print("    시간 장소<br>")
    for log in log_set:
        log_time = log[0]
        device_id = log[1]
        strtime = time.strftime('%Y.%m.%d %H:%M:%S',
                                time.localtime(log_time))
        print("    {0} {1}<br>".format(strtime, device_id))
    print("  </p>")
    print("  <a href='/index.html'> Return to mainpage </a>")
    print("</body>")
    print("</html>")


# 응답 헤더
print("Content-type:text/html\r\n\r\n")
# 유저 학번
form = cgi.FieldStorage()
user_id = form.getvalue('id')
# 유저 학번 에러 방지
if user_id == None:
    user_id = ' '
# ini 파일 읽어오기
config_file = 'class_server.ini' # 하드 코딩
config = configparser.ConfigParser()
config.read(config_file)
# 변수 생성
user_db = config['server']['user_db']
# 데이터베이스 연결
connector = sqlite3.connect(user_db)
cursor = connector.cursor()
# 유저 맥주소 확인
try:
    cursor.execute('SELECT mac FROM user WHERE id=' + user_id)
    mac = cursor.fetchone()
except sqlite3.OperationalError:
    mac = None
# 등록된 유저가 없을 경우
if mac == None:
    _fail_response(user_id)
    sys.exit(0)
else:
    mac = mac[0]
# 변수 생성
scan_db = config['handle']['scan_db']
# 데이터베이스 연결
connector = sqlite3.connect(scan_db)
cursor = connector.cursor()
# 유저 기록 불러오기
cursor.execute('SELECT unix_time, device_id FROM scan '
              + 'WHERE log_set LIKE "%' + mac + '%" '
              + 'ORDER BY unix_time ASC')
log_set = cursor.fetchall()
# 유저 기록이 없을 경우
if log_set == None:
    log_set = [(int(time.time()), '기록없음')]
_success_response(user_id, log_set)
