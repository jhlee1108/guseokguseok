#!/usr/bin/python3

import configparser # ConfigParser
import socket # socket
import os # path.exists
import sys # exit
import struct # unstruct
import logging # log

class BaseScanner(object):
    """MAC 주소를 스캔하는 클래스
    """
    # 스니핑 소켓 생성
    # @arg: socket - interface 가 있는 config
    def _create_socket(self):
        # 소켓 생성시 예외 발생 가능
        try:
            # 소켓 생성
            self.read_socket = socket.socket(family=socket.AF_PACKET, \
                    type=socket.SOCK_RAW)
            # 인터페이스, 이더넷 종류
            # https://linux.die.net/include/linux/if_ether.h
            socket_interface = (self.config['socket'])['interface']
            socket_ethernet = 0x0004 # Every packet (be careful!!!)
            # 소켓 바인드
            self.read_socket.bind((socket_interface, socket_ethernet))
        except Exception as err:
            logging.error('create socket 예외 발생')
            sys.exit(0)

    # 맥 주소 파싱
    # @arg: 스니핑 소켓
    def _get_readed_mac(self):
        # 읽을 데이터가 없을 떄를 위해 타임 아웃 설정
        timeout = int(self.config['socket']['timeout'])
        self.read_socket.settimeout(timeout)
        # 타임 아웃 예외 발생 가능
        try:
            # WLAN 802.11 MTU(2304) + WPA-TKIP(20)
            # https://en.wikipedia.org/wiki/Maximum_transmission_unit
            read_data = self.read_socket.recv(2324)
            # MAC 주소 파싱
            read_mac, read_ssi_signal = self._parse_data(read_data)
        except socket.timeout:
            logging.debug('Socket timeout')
            return None, None
        # MAC 주소 반환
        return read_mac, read_ssi_signal

    # Probe Request의 MAC 주소 파싱
    def _parse_data(self, read_data):
        # bytes 형만 파싱
        if type(read_data) != bytes:
            logging.error('parse_data 에 주어진 read_data 가 bytes '
                          + '타입이 아닙니다.')
            return None, None
        # 데이터 커서 생성
        data_cursor = read_data
        if len(data_cursor) < 8:
            return None, None
        # radiotab header length
        # http://www.radiotap.org/
        radiotab = struct.unpack('!1s1s2s4s', data_cursor[0:8])
        radiotab_length = int.from_bytes(radiotab[2], byteorder='little')
        # ssi_signal 계산
        ssi_signal = data_cursor[22]
        ssi_signal = ssi_signal - 256 if ssi_signal > 127 else ssi_signal
        # 데이터 커서 이동
        data_cursor = data_cursor[radiotab_length:]
        if len(data_cursor) < 22:
            return None, None
        # 802.11 frame
        frame80211 = struct.unpack('!2s2s6s6s6s', data_cursor[0:22])
        # probe request
        frame_control_field = frame80211[0].hex()
        subtype = frame_control_field[0]
        frame_type = frame_control_field[1]
        if subtype != '4' or frame_type != '0': # Type: Management frame(0)
            return None, None                   # Subtype: 4
        source_mac_address = frame80211[3].hex()
        print('SSI Signal: %d dBm' % ssi_signal)
        print('Frame Control Field: ' + frame_control_field)
        print('Source address: ' + source_mac_address)
        # MAC 주소 반환
        return source_mac_address, ssi_signal

    def _handle_mac(self, mac, ssi_signal):
        # 맥 주소 핸들링
        # 각 기록기에서 새로 구현해야 함
        raise NotImplementedError

    # 스캔 시작
    def start_scan(self):
        # 소켓 생성
        self._create_socket()
        # 종료를 위한 try-catch
        try:
            logging.info('모니터링을 시작합니다.')
            logging.info('중지하려면 Ctrl + C를 누르세요.')
            # 데이터 읽기
            while True:
                mac, ssi_signal = self._get_readed_mac()
                if mac == None: # MAC 주소가 안 읽힐 수 있음
                    continue
                # 읽은 맥주소 다루기
                self._handle_mac(mac, ssi_signal)
        except KeyboardInterrupt:
            logging.info('모니터링을 중지합니다.')
            sys.exit(0)

    # 초기화: 설정 파일 불러오기
    # 베이스 스캐너는 상속자마다 설정 파일이 다를 수 있기 때문에
    # 설정 파일을 인자로 받음
    def __init__(self, config_file):
        # dict 타입 config_file 고려 for unit testing
        if type(config_file) == dict:
            self.config = config_file
        # 설정 파일 확인
        if not os.path.exists(config_file):
            logging.critical('Config file does not exists: {0}'.format(
                             config_file))
            sys.exit(0)
        # 설정파일 읽기
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        # 로그 설정 파일 확인
        if not 'log' in self.config:
            logging.critical('설정 파일에 log 세션이 필요합니다.')
            sys.exit(0)
        if not 'level' in self.config['log']:
            logging.critical('설정 파일 log 세션에 '
                            + 'level 항목이 필요합니다.')
            sys.exit(0)
        if not 'file' in self.config['log']:
            logging.critical('설정 파일 log 세션에 '
                             + 'file 항목이 필요합니다.')
            sys.exit(0)
        # 로그 레벨, 파일 이름 불러오기
        log_level = getattr(logging, self.config['log']['level'])
        log_file = self.config['log']['file']
        # 로그 레벨 세팅
        logging.basicConfig(filename = log_file,
                            level = log_level,
                            format = '%(asctime)s '
                                   + '%(levelname)s: '
                                   + '%(message)s',
                            datefmt = '%Y.%m.%d %H:%M:%S')
        # 소켓 설정 파일 확인
        if not 'socket' in self.config:
            logging.critical('설정 파일에 socket 세션이 필요합니다.')
            sys.exit(0)
        if not 'interface' in self.config['socket']:
            logging.critical('설정 파일 socket 세션에'
                             + 'interface 항목이 필요합니다.')
            sys.exit(0)
        if not 'timeout' in self.config['socket']:
            logging.critical('설정 파일 socket 세션에'
                             + 'timeout 항목이 필요합니다.')
            sys.exit(0)
