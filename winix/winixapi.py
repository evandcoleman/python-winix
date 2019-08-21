import json
import logging
import requests
import time
import collections
import base64
import binascii
from datetime import datetime
from urllib.parse import parse_qs, urlparse, quote

from winix.devices.purifier import Purifier
from winix.util.cipher import AESCipher
from winix.util.discovery import Discovery

BASE_URI = 'https://smart.us.gw.winixcorp.com:9903'

SIGN_IN = 'user/login/v1'
STATUS = 'homedevice/list'
CONTROL = 'homedevice/control'

REFRESHTIME = 60 * 60 * 12
_LOGGER = logging.getLogger(__name__)

class WinixSession:

    username = ''
    password = ''
    serverUId = ''
    devices = []

SESSION = WinixSession()

class WinixApi:

    def __init__(self, username, password):
        SESSION.username = username
        SESSION.password = password

        if username is None or password is None:
            return None
        else:
            self.login()
            self.discover_devices()

    def devices(self):
        return SESSION.devices

    def login(self):
        SESSION.serverUId = self._authenticate()
        # access_token, refresh_token = self._get_token(code)
        # SESSION.access_token = access_token
        # SESSION.refresh_token = refresh_token

    def _authenticate(self):
        cipher = AESCipher('winixpurifier152')
        enc = cipher.encrypt(SESSION.password)
        response = self._request(SIGN_IN, {
            'userId': SESSION.username,
            'userPwd': enc.decode()
        })
        json = response.json()

        return json['body']['auth']['serverUId']

    def discover_devices(self):
        discovery = Discovery()
        device_ids = discovery.discover_devices()
        SESSION.devices = list(map(lambda x: Purifier(x, self), device_ids))
        print(SESSION.devices)

    def refresh_devices(self):
        for device in SESSION.devices:
            device.refresh()

    def device_status(self, device):
        response = self._request(STATUS, {
            'hDIds': device.device_id,
            'hDList': 'N'
        })
        return response.json()['body']['homeDevice']['list'][0]

    def control(self, device, command):
        response = self._request(CONTROL, {
            'hDId': device.device_id,
            'flag': 'N',
            'controlData': command
        })

    def _request(self, endpoint, params):
        message = {
            'header': {
                'deviceId': '2F48BC7C-85A2-4408-866C-BA4ED1CDD9A5',
                'reqTime': datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3],
                'osKind': 'IOS',
                'networkKind': 'WIFI',
                'osVer': '12.4',
                'modelName': 'iPhone11,2',
                'langCode': 'EN',
                'resolution': '320*568',
                'serverUId': SESSION.serverUId
            },
            'body': params
        }
        print(message)
        return requests.post(
            BASE_URI + '/' + endpoint,
            headers= {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Accept-Language': 'en-us'
            },
            data= json.dumps(message)
        )

    def check_access_token(self):
        if SESSION.username == '' or SESSION.password == '':
            raise WinixAPIException("can not find username or password")
            return
        if SESSION.serverUId == '':
            self.login()

    def poll_devices_update(self):
        self.check_access_token()
        self.refresh_devices()

    def get_all_devices(self):
        return SESSION.devices

    def get_device_by_id(self, dev_id):
        for device in SESSION.devices:
            if device.device_id() == dev_id:
                return device
        return None


class WinixAPIException(Exception):
    pass
