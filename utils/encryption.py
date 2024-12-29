# from config.server_variables import MYSQL_SECRET_KEY
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import base64
import bcrypt

# Clave de cifrado de 32 bytes (256 bits)
# KEY = ENCRYPTION_KEY.encode()
KEY = b'$}r\xfe\xe8\x1f\x17a\x8b\x1e\xd4\xc2\xd9\x9b\x82e`.\xb8U\t\xe7\x1d\x90p\xab\x8f}Vdgn'

def pad(s):
    return s + (16 - len(s) % 16) * ' '

def unpad(s):
    return s.rstrip()

def encrypt_data(data, key=KEY):
    print(KEY)
    print(type(KEY))
    data = pad(data)
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(data.encode())
    return base64.b64encode(iv + encrypted).decode('utf-8')

def decrypt_data(encrypted_data, key=KEY):
    print(KEY)
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted_data[16:]).decode('utf-8')
    return unpad(decrypted)

def hash_password(password, salt):
    if type(salt) == str:
        salt = salt.encode()
    hashed_data = bcrypt.hashpw(password.encode(), salt).decode('utf-8')
    return hashed_data

def hash_data(data):
    h = SHA256.new()
    h.update(data.encode())
    return h.hexdigest()