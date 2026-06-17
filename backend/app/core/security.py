import base64
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import jwt as jose_jwt, JWTError

from app.config import settings


NONCE_LENGTH = 12


def _decode_key(key_b64: str) -> bytes:
    if not key_b64:
        raise ValueError("Encryption key is empty")
    key = base64.b64decode(key_b64)
    if len(key) != 32:
        raise ValueError(f"Encryption key must be 32 bytes, got {len(key)}")
    return key


def encrypt_bytes(plaintext: str, key_b64: str) -> bytes:
    key = _decode_key(key_b64)
    payload = json.dumps({"v": plaintext}, ensure_ascii=False).encode("utf-8")
    nonce = os.urandom(NONCE_LENGTH)
    aes = AESGCM(key)
    ciphertext_and_tag = aes.encrypt(nonce, payload, None)
    return nonce + ciphertext_and_tag


def decrypt_bytes(ciphertext: bytes, key_b64: str) -> str:
    key = _decode_key(key_b64)
    if len(ciphertext) <= NONCE_LENGTH + 16:
        raise ValueError("Ciphertext too short")
    nonce = ciphertext[:NONCE_LENGTH]
    ct = ciphertext[NONCE_LENGTH:]
    aes = AESGCM(key)
    raw = aes.decrypt(nonce, ct, None)
    data = json.loads(raw.decode("utf-8"))
    if isinstance(data, dict) and "v" in data:
        return str(data["v"])
    if isinstance(data, str):
        return data
    raise ValueError("Decrypted payload format invalid")


def encrypt_for_storage(plaintext: str) -> bytes:
    return encrypt_bytes(plaintext, settings.MESSAGE_ENCRYPTION_KEY)


def decrypt_for_storage(ciphertext: bytes) -> str:
    return decrypt_bytes(ciphertext, settings.MESSAGE_ENCRYPTION_KEY)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: str, role: str, display_name: str) -> str:
    expire = _utcnow() + timedelta(minutes=settings.JWT_ACCESS_TTL_MINUTES)
    to_encode = {
        "sub": user_id,
        "role": role,
        "display_name": display_name,
        "exp": expire,
        "type": "access",
        "iat": _utcnow(),
    }
    return jose_jwt.encode(to_encode, settings.JWT_ACCESS_SECRET, algorithm="HS256")


def create_refresh_token(user_id: str) -> str:
    expire = _utcnow() + timedelta(days=settings.JWT_REFRESH_TTL_DAYS)
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
        "iat": _utcnow(),
    }
    return jose_jwt.encode(to_encode, settings.JWT_REFRESH_SECRET, algorithm="HS256")


def decode_jwt(token: str) -> Optional[dict]:
    if not token:
        return None
    try:
        payload = jose_jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        try:
            payload = jose_jwt.decode(token, settings.JWT_REFRESH_SECRET, algorithms=["HS256"])
            return payload
        except JWTError:
            return None
    except Exception:
        return None


def hash_password(password: str) -> str:
    salted = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return salted.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False
