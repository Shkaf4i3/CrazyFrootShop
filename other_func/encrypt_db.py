from pathlib import Path

from aiofiles import open
from cryptography.fernet import Fernet

PATH_TO_FILE = Path(__file__).parent.parent / "files"
PATH_TO_FILE.mkdir(exist_ok=True)


async def generate_crypto_key() -> bytes:
    key = Fernet.generate_key()

    async with open(file=PATH_TO_FILE / "test.txt", mode="wb") as file:
        await file.write(key)


    return key


async def get_crypto_key() -> bytes:
    async with open(file=PATH_TO_FILE / "test.txt", mode="rb") as file:
        key = await file.read()
        return key


def encrypt_password(password: str, key: bytes) -> bytes:
    fernet = Fernet(key=key)
    encrypt_password = fernet.encrypt(data=password.encode())

    return encrypt_password


def decrypt_password(password: bytes, key: bytes) -> str:
    fernet = Fernet(key=key)
    decrypt_password = fernet.decrypt(token=password).decode()

    return decrypt_password
