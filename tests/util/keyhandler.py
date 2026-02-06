import warnings
import os
import tomllib
from pathlib import Path
from typing import Any, Optional, TypeVar

from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode


def str_2_key(gen: str) -> bytes:
    if not gen:
        warnings.warn("No key supplied!")
    if (length := len(gen)) < 32:
        warnings.warn(f"Short length {length}")
        gen = gen.zfill(32)
    elif length > 32:
        warnings.warn(f"Long length {length}")
        gen = gen[:32]

    return urlsafe_b64encode(gen.encode())


_fernet_key_raw = os.getenv("FERNET_KEY")
FERNET_KEY = str_2_key(_fernet_key_raw) if _fernet_key_raw is not None else Fernet.generate_key()
FERNET = Fernet(FERNET_KEY)

T = TypeVar("T")


def _decrypt_val(v: T) -> T:
    if isinstance(v, str):
        return FERNET.decrypt(v).decode()  # type: ignore
    if isinstance(v, list):
        return _decrypt_list(v)  # type: ignore
    if isinstance(v, dict):
        return _decrypt_dict(v)  # type: ignore

    return v


def _decrypt_list(data: list) -> list:
    ret = []
    for v in data:
        ret.append(_decrypt_val(v))
    return ret


def _decrypt_dict(data: dict) -> dict:
    ret = {}
    for k, v in data.items():
        ret[k] = _decrypt_val(v)

    return ret


__fp__ = Path(__file__).parent

_auth_fp = __fp__ / "auth.toml"
_local_auth_fp = __fp__ / "local_auth.toml"

_cached_auth: Optional[dict[str, Any]] = None

def get_auth() -> dict[str, Any]:
    try:
        _auth = _decrypt_dict(tomllib.load(_auth_fp.open("rb")))
    except Exception:
        _auth = {}

    _local_auth = tomllib.load(_local_auth_fp.open("rb")) if _local_auth_fp.exists() else {}

    _cached_auth = _auth | _local_auth
    
    return _cached_auth

def mask_secret(secret: str):
    warnings.warn(f"::add-mask::{secret}")
