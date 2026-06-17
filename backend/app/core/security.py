"""
安全模块：密码哈希、JWT、AES 加密
"""

import base64
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

import bcrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import jwt as jose_jwt, JWTError

from app.config import settings


NONCE_LENGTH = 12


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_key_bytes(key_b64_or_plain: str) -> bytes:
    """接受 base64 编码的 32 字节密钥，或普通字符串自动补齐到 32 字节"""
    if not key_b64_or_plain:
        raise ValueError("加密密钥为空")
    # 先尝试作为 base64 解码
    try:
        key = base64.b64decode(key_b64_or_plain)
        if len(key) == 32:
            return key
    except Exception:
        pass
    # 如果是普通字符串，直接编码
    raw = key_b64_or_plain.encode("utf-8")
    if len(raw) >= 32:
        return raw[:32]
    # 不足则补齐
    return raw + b"\x00" * (32 - len(raw))


# ========== AES-256-GCM 加密 ==========

def aes_encrypt(plaintext: str, key_b64: str) -> bytes:
    """加密字符串为 bytes（nonce + ciphertext + tag）"""
    key = _ensure_key_bytes(key_b64)
    payload = json.dumps({"v": plaintext}, ensure_ascii=False).encode("utf-8")
    nonce = os.urandom(NONCE_LENGTH)
    aes = AESGCM(key)
    ciphertext_and_tag = aes.encrypt(nonce, payload, None)
    return nonce + ciphertext_and_tag


def aes_decrypt(ciphertext: bytes, key_b64: str) -> str:
    """解密 bytes 为字符串"""
    key = _ensure_key_bytes(key_b64)
    if len(ciphertext) <= NONCE_LENGTH + 16:
        raise ValueError("密文太短")
    nonce = ciphertext[:NONCE_LENGTH]
    ct = ciphertext[NONCE_LENGTH:]
    aes = AESGCM(key)
    raw = aes.decrypt(nonce, ct, None)
    data = json.loads(raw.decode("utf-8"))
    if isinstance(data, dict) and "v" in data:
        return str(data["v"])
    if isinstance(data, str):
        return data
    raise ValueError("解密后的载荷格式无效")


def encrypt_for_storage(plaintext: str) -> bytes:
    return aes_encrypt(plaintext, settings.get_aes_key())


def decrypt_for_storage(ciphertext: bytes) -> str:
    return aes_decrypt(ciphertext, settings.get_aes_key())


# ========== JWT ==========

def create_jwt(user_id: str, role: str, display_name: str = "") -> Dict[str, str]:
    """创建 access_token 和 refresh_token"""
    # access token
    access_exp = _utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    access_payload = {
        "user_id": user_id,
        "role": role,
        "display_name": display_name,
        "exp": access_exp,
        "type": "access",
        "iat": _utcnow(),
    }
    access_token = jose_jwt.encode(
        access_payload,
        settings.get_jwt_secret(),
        algorithm=settings.JWT_ALGORITHM,
    )

    # refresh token
    refresh_exp = _utcnow() + timedelta(days=settings.JWT_REFRESH_TTL_DAYS)
    refresh_payload = {
        "user_id": user_id,
        "role": role,
        "exp": refresh_exp,
        "type": "refresh",
        "iat": _utcnow(),
    }
    refresh_token = jose_jwt.encode(
        refresh_payload,
        settings.get_refresh_secret(),
        algorithm=settings.JWT_ALGORITHM,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def create_access_token(user_id: str, role: str, display_name: str = "") -> str:
    """仅创建 access token（兼容旧 API）"""
    exp = _utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "role": role,
        "display_name": display_name,
        "exp": exp,
        "type": "access",
        "iat": _utcnow(),
    }
    return jose_jwt.encode(
        payload,
        settings.get_jwt_secret(),
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(user_id: str, role: str = "") -> str:
    exp = _utcnow() + timedelta(days=settings.JWT_REFRESH_TTL_DAYS)
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": exp,
        "type": "refresh",
        "iat": _utcnow(),
    }
    return jose_jwt.encode(
        payload,
        settings.get_refresh_secret(),
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_jwt(token: str) -> Optional[dict]:
    """解码 JWT token"""
    if not token:
        return None
    # 移除 Bearer 前缀
    if token.lower().startswith("bearer "):
        token = token[7:]
    # 依次尝试 access 和 refresh 密钥
    for secret in [settings.get_jwt_secret(), settings.get_refresh_secret()]:
        try:
            payload = jose_jwt.decode(
                token,
                secret,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except JWTError:
            continue
        except Exception:
            continue
    return None


# ========== 密码 ==========

def hash_password(password: str) -> str:
    """bcrypt 哈希密码"""
    salted = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return salted.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """验证密码"""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False
