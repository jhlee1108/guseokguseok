#!/usr/bin/python3

import configparser
import sys
import os
import stat
import logging
import sqlite3
import urllib.parse # urlunparse
from http.server import HTTPServer
from http.server import CGIHTTPRequestHandler
import time


INIFILE = 'class_server.ini'


class ClassScannerServerHandler(CGIHTTPRequestHandler):
    # 초기화
    # 데이터베이스 이름 확인
    config_file = INIFILE
    config = configparser.ConfigParser()
    config.read(config_file)
    scan_db = config['handle']['scan_db']
    # 데이터베이스 연결
    connector = sqlite3.connect(scan_db)
    cursor = connector.cursor()
        
    # POST
    def do_POST(self):
        # 홈페이지
        if self.path != '/':
            CGIHTTPRequestHandler.do_POST(self)
            return
        # 응답 전송
        self.send_response(200)
        self.end_headers()
        try:
            # 전송받은 데이터 파싱
            data = self.rfile.read()
            data = data.decode('utf-8')
            data = urllib.parse.parse_qs(data)
            # 저장할 데이터 준비
            unix_time = int(time.time())
            device_id = data['device_id'][0]
            log_set = data['log_set'][0]
            # 데이터베이스 커밋
            self.cursor.execute('''
                    INSERT OR IGNORE INTO scan
                    (unix_time, device_id, log_set) VALUES ('''
                    + str(unix_time) + ', '
                    + '"' + device_id + '", '
                    + '"' + log_set + '")')
            self.connector.commit()
            # 성공 응답 전송
            self.send_response(202)
            self.end_headers()
        except Exception as err:
            logging.error(err)
            # 실패 응답 전송
            self.send_response(400)
            self.end_headers()

    # print nothing!
    def log_message(self, format, *args):
        logging.debug('{0} {1} {2}'.format(
                     self.client_address, self.command, self.path))
        return

def main():
    """HTTP 서버 데몬 생성
    """
    # ini 파일 위치 확인
    config_file = INIFILE
    config = configparser.ConfigParser()
    config.read(config_file)
    # ini 서버 옵션
    if not 'server' in config:
        logging.critical('설정 파일에 server 세션이 필요합니다.')
        sys.exit(0)
    if not 'port' in config['server']:
        logging.critical('설정 파일 server 세션에 '
                        + 'port 항목이 필요합니다.')
        sys.exit(0)
    if not 'user_db' in config['server']:
        logging.critical('설정 파일 server 세션에 '
                        + 'user_db 항목이 필요합니다.')
        sys.exit(0)
    # 변수 생성
    http_port = int(config['server']['port'])
    user_db = config['server']['user_db']
    # 데이터베이스 생성 후 권한 설정
    connector = sqlite3.connect(user_db)
    os.chmod(user_db, 0o666)
    cursor = connector.cursor()
    cursor.executescript('''
            CREATE TABLE IF NOT EXISTS user
            ( id INTEGER PRIMARY KEY NOT NULL UNIQUE,
            mac TEXT );
            ''')
    connector.commit()
    cursor.close()
    # ini 핸들 옵션
    if not 'handle' in config:
        logging.critical('설정 파일에 handle 세션이 필요합니다.')
        sys.exit(0)
    if not 'scan_db' in config['handle']:
        logging.critical('설정 파일 handle 세션에 '
                        + 'scan_db 항목이 필요합니다.')
        sys.exit(0)
    # 내부 변수
    scan_db = config['handle']['scan_db']
    # 데이터베이스 생성 후 권한 설정
    connector = sqlite3.connect(scan_db)
    os.chmod(scan_db, 0o666)
    cursor = connector.cursor()
    cursor.executescript('''
            CREATE TABLE IF NOT EXISTS scan
            ( log_number INTEGER PRIMARY KEY AUTOINCREMENT,
            unix_time INTEGER,
            device_id TEXT,
            log_set TEXT );
            ''')
    connector.commit()
    cursor.close()
    # ini 로그 옵션
    if not 'log' in config:
        logging.critical('설정 파일에 log 세션이 필요합니다.')
        sys.exit(0)
    if not 'level' in config['log']:
        logging.critical('설정 파일 log 세션에 '
                        + 'level 항목이 필요합니다.')
        sys.exit(0)
    if not 'file' in config['log']:
        logging.critical('설정 파일 log 세션에 '
                        + 'file 항목이 필요합니다.')
        sys.exit(0)
    # 로그 레벨, 파일 이름 불러오기
    log_level = getattr(logging, config['log']['level'])
    log_file = config['log']['file']
    # 로그 레벨 세팅
    logging.basicConfig(filename = log_file,
                        level = log_level,
                        format = '%(asctime)s '
                               + '%(levelname)s:'
                               + '%(message)s',
                        datefmt = '%Y.%m.%d %H:%M:%S')
    # HTTP 데몬 생성
    try:
        logging.info('서버를 시작합니다. 중지하려면 Ctrl+C를 누르세요.')
        class_scanner_server = HTTPServer(('', http_port),
                                          ClassScannerServerHandler)
        class_scanner_server.serve_forever()
    except KeyboardInterrupt:
        logging.info('서버를 중지합니다.')

if __name__ == '__main__':
    main()
