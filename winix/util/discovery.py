from socket import *
from retrying import retry
import sys
import time
import binascii

class Discovery:

  def __init__(self):
    self._sock = socket(AF_INET, SOCK_DGRAM)
    self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    self._sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    self._sock.settimeout(3)
    # self._sock.connect(("8.8.8.8", 80))
    # print(self._sock.__dict__)
    # self._sock.close()

    self._server_address = ('10.255.255.255', 47556)
    self._message = 'I&C Technology'

  def retry_if_no_devices(result):
    """Return True if we should retry (in this case when result is None), False otherwise"""
    return len(result) == 0

  @retry(retry_on_result=retry_if_no_devices, stop_max_delay=600000, wait_fixed=5000)
  def discover_devices(self):
    device_ids = []

    try:
      while True:
        sent = self._sock.sendto(self._message.encode(), self._server_address)
        data, server = self._sock.recvfrom(4096)
        chunks = data.split(b'\x00' * 18)
        mac_address = ':'.join('%02X' % b for b in chunks[1][10:16])
        device_id = chunks[1][16:].decode('utf8')
        device_ids.append(device_id + mac_address)
    except timeout:  
      pass
    self._sock.close()

    return list(dict.fromkeys(device_ids))