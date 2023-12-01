import base64
from Crypto.Cipher import AES
import hashlib
import random
import string
import time
from urllib.parse import urlparse, quote


# based on https://github.com/retroplasma/flyover-reverse-engineering
# MIT(?)


class Authenticator:
    """
    Various requests to internal Apple Maps endpoints, such as Look Around imagery, must be
    dynamically authenticated with a session ID and access key.
    This class provides this functionality.
    """
    TOKEN_P1 = "4cjLaD4jGRwlQ9U"
    TOKEN_P2 = "72xIzEBe0vHBmf9"

    def __init__(self):
        self.session_id = _generate_session_id()

    def authenticate_url(self, url: str) -> str:
        """
        Appends authentication parameters to a URL.

        :param url: An unauthenticated URL.
        :return: An authenticated URL.
        """
        url_obj = urlparse(url)

        token_p3 = _generate_token_p3()
        token = self.TOKEN_P1 + self.TOKEN_P2 + token_p3
        timestamp = int(time.time()) + 4200
        separator = "&" if url_obj.query else "?"

        url_path = url_obj.path
        if url_obj.query:
            url_path += "?" + url_obj.query
        plaintext = f"{url_path}{separator}sid={self.session_id}{timestamp}{token_p3}"
        plaintext_bytes = _pad_pkcs7(plaintext.encode("utf-8"))
        key = hashlib.sha256(token.encode()).digest()
        iv = b"\0" * 16
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(plaintext_bytes)
        ciphertext_b64 = base64.b64encode(ciphertext).decode()
        ciphertext_url = quote(ciphertext_b64, safe="")
        access_key = f"{timestamp}_{token_p3}_{ciphertext_url}"
        final = f"{url}{separator}sid={self.session_id}&accessKey={access_key}"
        return final


def _generate_session_id() -> str:
    return ''.join(random.choices(string.digits, k=40))


def _generate_token_p3() -> str:
    return ''.join(random.choices(string.digits + string.ascii_lowercase + string.ascii_uppercase, k=16))


def _pad_pkcs7(data, block_size: int = 16):
    if type(data) != bytearray and type(data) != bytes:
        raise TypeError()
    padding_size = block_size - (len(data) % block_size)
    padding = bytearray([padding_size] * padding_size)
    return data + padding
