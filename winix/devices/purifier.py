import time
import collections
from base64 import b64decode

SPEED_SLEEP = 'sleep'
SPEED_LOW = 'low'
SPEED_MEDIUM = 'medium'
SPEED_HIGH = 'high'
SPEED_TURBO = 'turbo'

speed_map = {
    SPEED_SLEEP : '8',
    SPEED_LOW : '4',
    SPEED_MEDIUM : '5',
    SPEED_HIGH : '6',
    SPEED_TURBO : '7',
}

class Purifier(object):
    def __init__(self, device_id, api):
        self.api = api
        self.device_id = device_id
        self.refresh()

    def refresh(self):
        status = self.api.device_status(self)
        self.name = status['nickName']
        self.model_name = status['modelName']
        self.firmware_version = status['firmwareVer']

        data = b64decode(status['byteData'])
        control = list(map(int, list(bin(data[0])[2:])))
        air = list(map(int, list(bin(data[2])[2:])))
        
        self.air_quality_index = int(data[10])
        self.is_on = control[0] == 1
        self.is_auto = control[1] == 1
        self.is_light_on = control[7] == 1
        self.is_plasma_on = air[3] == 1

        if control[2] == 1:
            self.fan_speed = SPEED_LOW
        elif control[3] == 1:
            self.fan_speed = SPEED_MEDIUM
        elif control[4] == 1:
            self.fan_speed = SPEED_HIGH
        elif control[5] == 1:
            self.fan_speed = SPEED_TURBO
        else:
            self.fan_speed = SPEED_SLEEP

    def set_power(self, on):
        self.is_on = on
        self.api.control(self, '1' if on else '2')
        self.refresh()

    def set_auto_mode(self, on):
        self.is_auto = on
        self.api.control(self, '3' if on else '19')
        self.refresh()

    def set_fan_speed(self, speed):
        self.fan_speed = speed
        self.is_auto = False
        self.api.control(self, speed_map[speed])
        self.refresh()

    def toggle_light(self):
        self.is_light_on = !self.is_light_on
        self.api.control(self, '9')
        self.refresh()

    def toggle_plasma(self):
        self.is_plasma_on = !self.is_plasma_on
        self.api.control(self, '17')
        self.refresh()
