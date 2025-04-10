from cryptography.fernet import Fernet
import base64
import hashlib

def create_key(password: str) -> bytes:
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt_note(text: str, password: str) -> str:
    f = Fernet(create_key(password))
    return f.encrypt(text.encode()).decode()

def decrypt_note(encrypted_text: str, password: str) -> str:
    f = Fernet(create_key(password))
    return f.decrypt(encrypted_text.encode()).decode()
