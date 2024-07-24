from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64
import os

class EncryptionService:
    def __init__(self):
        self.key = base64.b64decode("MGE1OTVjN2M5Mjk2YzJkNzg3OTQ3MGYwMmRjZTcwOGU=")  # 16-byte key (base64 encoded for example)

    def encrypt_data(self, data):
        iv = os.urandom(16)  # Generate a random IV
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padded_data = padding.PKCS7(algorithms.AES.block_size).padder().update(data.encode()) + padding.PKCS7(algorithms.AES.block_size).padder().finalize()
        ct_bytes = encryptor.update(padded_data) + encryptor.finalize()
        iv_b64 = base64.b64encode(iv).decode('utf-8')
        ct_b64 = base64.b64encode(ct_bytes).decode('utf-8')
        return iv_b64, ct_b64

    def decrypt_data(self, iv_b64, ct_b64):
        iv = base64.b64decode(iv_b64)
        ct = base64.b64decode(ct_b64)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ct) + decryptor.finalize()
        plaintext = padding.PKCS7(algorithms.AES.block_size).unpadder().update(padded_plaintext) + padding.PKCS7(algorithms.AES.block_size).unpadder().finalize()
        return plaintext.decode()
