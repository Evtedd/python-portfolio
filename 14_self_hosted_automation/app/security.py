from cryptography.fernet import Fernet

from app.config import Settings


class SecretBox:
    def __init__(self, settings: Settings) -> None:
        key = settings.fernet_key.encode() if settings.fernet_key else Fernet.generate_key()
        self.fernet = Fernet(key)

    def encrypt(self, value: str) -> str:
        return self.fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt(self, value: str) -> str:
        return self.fernet.decrypt(value.encode("utf-8")).decode("utf-8")
