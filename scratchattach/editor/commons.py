"""
Shared functions used by the editor module
"""
from __future__ import annotations

import json
import random
import string
from typing import Optional, Final, Any

from ..utils import exceptions

DIGITS: Final[tuple[str]] = tuple("0123456789")

ID_CHARS: Final[str] = string.ascii_letters + string.digits  # + string.punctuation


# Strangely enough, it seems like something in string.punctuation causes issues. Not sure why


def _read_json_number(_str: str) -> float | int:
    ret = ''

    minus = _str[0] == '-'
    if minus:
        ret += '-'
        _str = _str[1:]

    def read_fraction(sub: str):
        sub_ret = ''
        if sub[0] == '.':
            sub_ret += '.'
            sub = sub[1:]
            while sub[0] in DIGITS:
                sub_ret += sub[0]
                sub = sub[1:]

        return sub_ret, sub

    def read_exponent(sub: str):
        sub_ret = ''
        if sub[0].lower() == 'e':
            sub_ret += sub[0]
            sub = sub[1:]

            if sub[0] in "-+":
                sub_ret += sub[0]
                sub = sub[1:]

            if sub[0] not in DIGITS:
                raise exceptions.UnclosedJSONError(f"Invalid exponent {sub}")

            while sub[0] in DIGITS:
                sub_ret += sub[0]
                sub = sub[1:]

        return sub_ret

    if _str[0] == '0':
        ret += '0'
        _str = _str[1:]

    elif _str[0] in DIGITS[1:9]:
        while _str[0] in DIGITS:
            ret += _str[0]
            _str = _str[1:]

    frac, _str = read_fraction(_str)
    ret += frac

    ret += read_exponent(_str)

    return json.loads(ret)


def consume_json(_str: str, i: int = 0) -> str | float | int | dict | list | bool | None:
    """
    *'gobble up some JSON until we hit something not quite so tasty'*

    Reads a JSON string and stops at the natural end (i.e. when brackets close, or when quotes end, etc.)
    """
    # Named by ChatGPT
    section = ''.join(_str[i:])
    if section.startswith("true"):
        return True
    elif section.startswith("false"):
        return False
    elif section.startswith("null"):
        return None
    elif section[0] in "0123456789.-":
        return _read_json_number(section)

    depth = 0
    json_text = ''
    out_string = True

    for char in section:
        json_text += char

        if char == '"':
            if len(json_text) > 1:
                unescaped = json_text[-2] != '\\'
            else:
                unescaped = True
            if unescaped:
                out_string ^= True
                if out_string:
                    depth -= 1
                else:
                    depth += 1

        if out_string:
            if char in "[{":
                depth += 1
            elif char in "}]":
                depth -= 1

        if depth == 0 and json_text.strip():
            return json.loads(json_text.strip())

    raise exceptions.UnclosedJSONError(f"Unclosed JSON string, read {json_text}")


def is_partial_json(_str: str, i: int = 0) -> bool:
    try:
        consume_json(_str, i)
        return True

    except exceptions.UnclosedJSONError:
        return False

    except ValueError:
        return False


def is_valid_json(_str: Any) -> bool:
    try:
        json.loads(_str)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def noneless_update(obj: dict, update: dict) -> None:
    for key, value in update.items():
        if value is not None:
            obj[key] = value


def remove_nones(obj: dict) -> None:
    """
    Removes all None values from a dict.
    :param obj: Dictionary to remove all None values.
    """
    nones = []
    for key, value in obj.items():
        if value is None:
            nones.append(key)
    for key in nones:
        del obj[key]


def safe_get(lst: list | tuple, _i: int, default: Optional[Any] = None) -> Any:
    if len(lst) <= _i:
        return default
    else:
        return lst[_i]


def trim_final_nones(lst: list) -> list:
    """
    Removes the last None values from a list until a non-None value is hit.
    :param lst: list which will **not** be modified.
    """
    i = len(lst)
    for item in lst[::-1]:
        if item is not None:
            break
        i -= 1
    return lst[:i]


def dumps_ifnn(obj: Any) -> str:
    if obj is None:
        return None
    else:
        return json.dumps(obj)


def gen_id() -> str:
    # The old 'naïve' method but that chances of a repeat are so miniscule
    # Have to check if whitespace chars break it
    # May later add checking within sprites so that we don't need such long ids (we can save space this way)
    return ''.join(random.choices(ID_CHARS, k=20))


def sanitize_fn(filename: str):
    """
    Removes illegal chars from a filename
    :return: Sanitized filename
    """
    # Maybe could import a slugify module, but it's a bit overkill
    ret = ''
    for char in filename:
        if char in string.ascii_letters + string.digits + "-_":
            ret += char
        else:
            ret += '_'
    return ret


def get_folder_name(name: str) -> str | None:
    if name.startswith('//'):
        return None

    if '//' in name:
        return name.split('//')[0]
    else:
        return None


def get_name_nofldr(name: str) -> str:
    """
    Get the sprite/asset name without the folder name
    """
    fldr = get_folder_name(name)
    if fldr is None:
        return name
    else:
        return name[len(fldr) + 2:]


class Singleton(object):
    _instance: Singleton

    def __new__(cls, *args, **kwargs):
        if hasattr(cls, "_instance"):
            return cls._instance
        else:
            cls._instance = super(Singleton, cls).__new__(cls)
            return cls._instance
