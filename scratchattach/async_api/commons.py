from typing_extensions import Final
import string

HEADERS: Final[dict[str, str]] = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-csrftoken": "a",
    "x-requested-with": "XMLHttpRequest",
    "referer": "https://scratch.mit.edu",
}

B62_CHARS: Final[str] = string.digits + string.ascii_uppercase + string.ascii_lowercase


def b62_decode(text: str) -> int:
    """
    Convert a base62 string into an int. This is used internally by the session id decoder.
    The session id format is defined in django's source code.
    """
    # the fact that scapi decided to change this into a 1 liner...
    # i don't think the one-liner has any efficiency gain -
    # it's literally just harder to read :/
    # but it's a good shout to make the chars into a constant i guess
    ret = 0
    for char in text:
        ret = ret * 62 + B62_CHARS.index(char)

    return ret
