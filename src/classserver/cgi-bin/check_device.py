#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import modules for CGI handling
import cgi, cgitb
cgitb.enable()
import sqlite3 # 데이터베이스 접근
import datetime # date_time 시간 변환
import sys # 종료
import configparser # 설정파일 읽기


def _fail_response():
    print("<html>")
    print("<head>")
    print("  <meta charset='UTF-8'>")
    print("  <title>DNLab 출석부</title>")
    print("</head>")
    print("<body>")
    print("  <h1>Fail</h1>")
    print("  <a href='/index.html'> Return to mainpage </a>")
    print("</body>")
    print("</html>")


def _success_response(devices):
    print("<html>")
    print("<head>")
    print("  <meta charset='UTF-8'>")
    print("  <title>DNLab 출석부</title>")
    print("</head>")
    print("<body>")
    print("  <h1>Success</h1>")
    print("  <p>")
    print("    device_id datetime<br>")
    for d in devices:
        cursor.execute('SELECT MAX(date_time), device_id FROM scan '
                     + 'WHERE device_id = "' + d[0] + '"')
        log = cursor.fetchone()
        log_time = log[0]
        device_id = log[1]
        strtime = datetime.datetime.strptime(str(log_time), '%Y%m%d%H%M%S')\
									.strftime('%Y.%m.%d %H:%M:%S')
        print("    {0} {1}<br>".format(device_id, strtime))
    print("  </p>")
    print("  <a href='/index.html'> Return to mainpage </a>")
    print("</body>")
    print("</html>")


print("Content-type:text/html\r\n\r\n")

config_file = 'class_server.ini' 
config = configparser.ConfigParser()
config.read(config_file)
scan_db = config['handle']['scan_db']

connector = sqlite3.connect(scan_db)
cursor = connector.cursor()

cursor.execute('SELECT DISTINCT device_id FROM scan')
devices = cursor.fetchall()

if len(devices) == 0:
    _fail_response()
    sys.exit(0)

_success_response(devices)
