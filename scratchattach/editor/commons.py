"""
Shared functions used by the editor module
"""
from __future__ import annotations

import json
import random
import string
from typing_extensions import Optional, Final, Any, TYPE_CHECKING, Union, Self, TypeVar
from enum import EnumMeta, Enum

if TYPE_CHECKING:
    from . import sprite, build_defaulting

    SpriteInput = Union[sprite.Sprite, build_defaulting._SetSprite]
else:
    SpriteInput = Any

T = TypeVar('T')
from scratchattach.utils import exceptions

DIGITS: Final[tuple[str, ...]] = tuple("0123456789")

# Strangely enough, it seems like something in string.punctuation causes issues. Not sure why
ID_CHARS: Final[str] = string.ascii_letters + string.digits  # + string.punctuation


def is_valid_json(_str: Any) -> bool:
    """
    Try to load a json string, if it fails, return False, else return true.
    """
    try:
        json.loads(_str)
        return True
    except (ValueError, TypeError):
        return False


def noneless_update(obj: dict, update: dict) -> None:
    """
    equivalent to dict.update, except and values of None are not assigned
    """
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
    """
    Like dict.get() but for lists
    """
    if len(lst) <= _i:
        return default
    else:
        return lst[_i]


def trim_final_nones(lst: list[T]) -> list[T]:
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


def dumps_ifnn(obj: Any) -> Optional[str]:
    """
    Return json.dumps(obj) if the object is not None
    """
    if obj is None:
        return None
    else:
        return json.dumps(obj)


def gen_id() -> str:
    """
    Generate an id for scratch blocks/variables/lists/broadcasts

    The old 'naïve' method but that chances of a repeat are so miniscule
    Have to check if whitespace chars break it
    May later add checking within sprites so that we don't need such long ids (we can save space this way)
    If this is implemented, we would need to be careful when merging sprites/adding blocks etc
    """
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
    """
    Get the name of the folder if this is a turbowarp-style costume name
    """
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


class SingletonMeta(EnumMeta):

    def __call__(self, value=0, *args, **kwds):
        if value != 0:
            raise ValueError("Value must be 0.")
        old_bases = self.__bases__
        self.__bases__ = old_bases + (Enum,)
        result = super().__call__(value, *args, **kwds)
        self.__bases__ = old_bases
        return result


if TYPE_CHECKING:
    Singleton = Enum
else:
    class Singleton(metaclass=SingletonMeta):

        def __new__(cls, val=None):
            if cls is Singleton:
                raise TypeError("Singleton cannot be created directly.")
            if hasattr(cls, "INSTANCE"):
                return getattr(cls, "INSTANCE")
            if val == 0:
                return super().__new__(cls)
            raise TypeError("Has no instance.")

        def __init__(self, *args, **kwds):
            pass

        def __repr__(self):
            return self.__class__.__name__

        def __str__(self):
            return self.__class__.__name__

        def __format__(self, format_spec):
            return str.__format__(str(self), format_spec)

        def __hash__(self):
            return hash(self.__class__)

        def __reduce_ex__(self, proto):
            return self.__class__, ()

        def __deepcopy__(self, memo):
            return self

        def __copy__(self):
            return self
