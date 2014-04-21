import base64
from flask import current_app
from Crypto.Cipher import AES
from Crypto import Random

def encrypt(message):
    """
    Encrypt a message using AES-CFB
    @param message the data to be encrypted
    @returns (ciphertext, iv) base64-encoded byte-strings
    """
    key = current_app.config['ENCRYPTION']['AES_KEY']
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    ciphertext = cipher.encrypt(message)
    return map(base64.b64encode, [ciphertext, iv])

def decrypt(ciphertext, iv):
    """
    Decrypt a ciphertext using AES-CFB
    @param message the ciphertext to decrypt, a base64-encoded byte-string
    @param iv the IV used for encryption

    @returns the original, encrypted message
    """
    ciphertext, iv = map(base64.b64decode, [ciphertext, iv])
    key = current_app.config['ENCRYPTION']['AES_KEY']
    cipher = AES.new(key, AES.MODE_CFB, iv)
    msg = cipher.decrypt(ciphertext)
    return msg
