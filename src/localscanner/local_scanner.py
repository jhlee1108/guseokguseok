#!/usr/bin/python3

from basescanner.base_scanner import BaseScanner
import logging
import sys
import os # chmod 
import time
import sqlite3
import hashlib # sha256


INIFILE = 'local_scanner.ini'


class LocalScanner(BaseScanner):
    """주위에서 읽은 MAC 주소를 출력 클래스
    """
    # 초기화
    def __init__(self, config_file):
        # 부모 클래스 초기화
        BaseScanner.__init__(self, config_file)
        # ini 파일 확인
        if not 'handle' in self.config:
            logging.critical('설정 파일에 handle 세션이 필요합니다.')
            sys.exit(0)
        if not 'interval' in self.config['handle']:
            logging.critical('설정 파일 handle 세션에 '
                             + 'interval 항목이 필요합니다.')
            sys.exit(0)
        if not 'scan_db' in self.config['handle']:
            logging.critical('설정 파일 handle 세션에 '
                             + 'scan_db 항목이 필요합니다.')
            sys.exit(0)
        # 내부 변수 초기화
        self.last_handle = int(time.time())
        self.log_set = set()
        self.interval = int(self.config['handle']['interval'])
        # 저장할 데이터베이스 생성
        scan_db = self.config['handle']['scan_db']
        self.connector = sqlite3.connect(scan_db)
        os.chmod(scan_db, 0o666)
        self.cursor = self.connector.cursor()
        self.cursor.executescript('''
                CREATE TABLE IF NOT EXISTS scan
                ( unix_time INTEGER PRIMARY KEY NOT NULL UNIQUE,
                log_set TEXT );
                ''')
        self.connector.commit()

    # MAC 주소 다루기
    def _handle_mac(self, mac):
        # 비식별화: 단방향 해쉬
        hash_object = hashlib.sha256()
        hash_object.update(mac.upper().encode('utf-8'))
        hashed_mac = hash_object.hexdigest()
        # 시간 비교용 변수
        now_handle = int(time.time())
        # 저장 셋에 추가
        self.log_set.add(hashed_mac)
        # 일정 시간마다 저장
        if (now_handle - self.last_handle) < self.interval:
            return
        # 데이터베이스 커밋
        self.cursor.execute('''
                INSERT OR IGNORE INTO scan
                (unix_time, log_set) VALUES ('''
                + str(now_handle) + ', '
                + '"' + str(self.log_set) + '")')
        self.connector.commit()
        logging.debug('Save Mac {0}'.format(len(self.log_set)))
        # 다음 저장 시간 세팅 및 변수 클리어
        self.last_handle = now_handle
        self.log_set.clear()


def main():
    config_file = INIFILE
    local_scanner = LocalScanner(config_file)
    local_scanner.start_scan()

if __name__ == '__main__':
    main()
