from base64 import b64decode
from base64 import b64encode
import hashlib

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class AESCipher:
    def __init__(self, key):
        self.key = key.encode('utf8')
        self.iv = b'1234567890abcdef'
        self.bs = 32

    def encrypt(self, message):
        data = hashlib.sha1(message.encode('utf8')).digest()        
        self.cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return b64encode(self.cipher.encrypt(pad(data, self.bs)))

    def decrypt(self, data):
        raw = b64decode(data)
        self.cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return unpad(self.cipher.decrypt(raw), self.bs)
