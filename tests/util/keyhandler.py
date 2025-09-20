import warnings
import os
import tomllib
from pathlib import Path
from typing import TypeVar

from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode


def str_2_key(gen: str) -> bytes:
    if (length := len(gen)) < 32:
        warnings.warn(f"Short length {length}")
        gen = gen.zfill(32)
    elif length > 32:
        warnings.warn(f"Long length {length}")
        gen = gen[:32]

    return urlsafe_b64encode(gen.encode())


_fernet_key_raw = os.getenv("FERNET_KEY")
FERNET_KEY = str_2_key(_fernet_key_raw)
FERNET = Fernet(FERNET_KEY)

T = TypeVar("T")


def _decrypt_val(v: T) -> T:
    if isinstance(v, str):
        return FERNET.decrypt(v).decode()
    if isinstance(v, list):
        return _decrypt_list(v)
    if isinstance(v, dict):
        return _decrypt_dict(v)

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
_auth = _decrypt_dict(tomllib.load(
    (__fp__ / "auth.toml").open("rb")
))
_local_auth = tomllib.load(
    (__fp__ / "localauth.toml").open("rb")
)

AUTH = _auth | _local_auth
