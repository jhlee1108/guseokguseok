#!/usr/bin/python3

from basescanner.base_scanner import BaseScanner
import logging
import sys
import os # chmod 
import datetime
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
        if not 'device_id' in self.config['handle']:
            logging.critical('설정 파일 handle 세션에 '
                             + 'device_id 항목이 필요합니다.')
            sys.exit(0)
        if not 'scan_db' in self.config['handle']:
            logging.critical('설정 파일 handle 세션에 '
                             + 'scan_db 항목이 필요합니다.')
            sys.exit(0)
        # 내부 변수 초기화
        # self.last_handle = int(time.time())
        # self.mac_list = list()
        # self.interval = int(self.config['handle']['interval'])
        self.device_id = self.config['handle']['device_id']
        # 저장할 데이터베이스 생성
        scan_db = self.config['handle']['scan_db']
        self.connector = sqlite3.connect(scan_db)
        os.chmod(scan_db, 0o666)
        self.cursor = self.connector.cursor()
        self.cursor.executescript('''
                CREATE TABLE IF NOT EXISTS scan
                ( log_number INTEGER PRIMARY KEY AUTOINCREMENT, 
                date_time INTEGER,
                device_id TEXT,
                hashed_mac TEXT, 
                mac_vendor TEXT, 
                ssi_signal INTEGER );
                ''')
        self.connector.commit()

    # MAC 주소 다루기
    def _handle_mac(self, mac, ssi_signal):
        # 비식별화: 단방향 해쉬
        hash_object = hashlib.sha256()
        hash_object.update(mac.upper().encode('utf-8'))
        hashed_mac = hash_object.hexdigest()
        # 시간 비교용 변수
        # now_handle = int(time.time())
        # 저장 리스트에 추가
        # self.mac_list.append([now_handle, hashed_mac, mac[:6], ssi_signal])
        # 일정 시간마다 저장
        # if (now_handle - self.last_handle) < self.interval:
        #     return
        # 데이터베이스 커밋
        # for row in self.mac_list:
        self.cursor.execute('''
                INSERT OR IGNORE INTO scan
                (date_time, device_id, hashed_mac, mac_vendor, ssi_signal) VALUES ('''
                + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + ', ' 
                + '"' + str(self.device_id) + '", '
                + '"' + str(hashed_mac) + '", ' 
                + '"' + str(mac[:6]) + '", ' 
                + str(ssi_signal) + ')')
        self.connector.commit()
        logging.debug('Save Mac {0}'.format(mac[:6]))
        # 다음 저장 시간 세팅 및 변수 클리어
        # self.last_handle = now_handle
        # self.mac_list.clear()


def main():
    config_file = INIFILE
    local_scanner = LocalScanner(config_file)
    local_scanner.start_scan()

if __name__ == '__main__':
    main()
