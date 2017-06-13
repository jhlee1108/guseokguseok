#!/usr/bin/python3

from basescanner.base_scanner import BaseScanner
import logging # log
import sys # exit
import time # group mac
import urllib.parse # urlencode
import urllib.request # urlopen
import hashlib # sha256


INIFILE = 'class_scanner.ini'


class ClassScanner(BaseScanner):
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
        if not 'server_url' in self.config['handle']:
            logging.critical('설정 파일 handle 세션에 '
                             + 'server_url 항목이 필요합니다.')
            sys.exit(0)
        if not 'device_id' in self.config['handle']:
            logging.critical('설정 파일 handle 세션에 '
                             + 'device_id 항목이 필요합니다.')
            sys.exit(0)
        # 내부 변수 초기화
        self.last_handle = int(time.time())
        self.log_set = set()
        self.interval = int(self.config['handle']['interval'])
        self.server_url = self.config['handle']['server_url']
        self.device_id = self.config['handle']['device_id']
        
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
        # 데이터 시리얼화
        send_data = {'device_id': self.device_id,
                     'log_set': self.log_set}
        send_data = urllib.parse.urlencode(send_data) # URL 형태로 변환
        send_data = send_data.encode('ascii') # bytes 로 변환
        send_request = urllib.request.Request(self.server_url, 
                                              data = send_data)
        try:
            with urllib.request.urlopen(send_request) as response:
                logging.debug('Send {0} MAC. Status: {1}'.format(
                              len(self.log_set), response.status))
                self.log_set.clear()
        except Exception as err:
            logging.error('MAC address send error: {0}'.format(err))
        # 다음 저장 시간 세팅 및 변수 클리어
        self.last_handle = now_handle


def main():
    config_file = INIFILE
    class_scanner = ClassScanner(config_file)
    class_scanner.start_scan()

if __name__ == '__main__':
    main()
