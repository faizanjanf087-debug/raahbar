from cryptography.fernet import Fernet

import config


def _fernet():
    if not config.VAULT_KEY:
        raise RuntimeError("VAULT_KEY set karein (.env ya Replit Secrets mein)")
    return Fernet(config.VAULT_KEY.encode())


def encrypt(text):
    return _fernet().encrypt(text.encode()).decode()


def decrypt(token):
    return _fernet().decrypt(token.encode()).decode()
