from typing import Optional
from http.cookiejar import CookieJar
from enum import Enum, auto
browsercookie_err = None
try:
    import browsercookie
except Exception as e:
    browsercookie = None
    browsercookie_err = e

class Browser(Enum):
    ANY = auto()
    FIREFOX = auto()
    CHROME = auto()
    EDGE = auto()
    SAFARI = auto()
    CHROMIUM = auto()
    EDGE_DEV = auto()
    VIVALDI = auto()

    
FIREFOX = Browser.FIREFOX
CHROME = Browser.CHROME
EDGE = Browser.EDGE
SAFARI = Browser.SAFARI
CHROMIUM = Browser.CHROMIUM
EDGE_DEV = Browser.EDGE_DEV
VIVALDI = Browser.VIVALDI
ANY = Browser.ANY

def cookies_from_browser(browser : Browser = ANY) -> dict[str, str]:
    """
    Import cookies from browser to login
    """
    if not browsercookie:
        raise browsercookie_err or ModuleNotFoundError()
    cookies : Optional[CookieJar] = None
    if browser == ANY:
        cookies = browsercookie.load()
    elif browser == FIREFOX:
        cookies = browsercookie.firefox()
    elif browser == CHROME:
        cookies = browsercookie.chrome()
    elif browser == EDGE:
        cookies = browsercookie.edge()
    elif browser == SAFARI:
        cookies = browsercookie.safari()
    elif browser == CHROMIUM:
        cookies = browsercookie.chromium()
    elif browser == EDGE_DEV:
        cookies = browsercookie.edge_dev()
    elif browser == VIVALDI:
        cookies = browsercookie.vivaldi()
    assert isinstance(cookies, CookieJar)
    return {cookie.name: cookie.value for cookie in cookies if "scratch.mit.edu" in cookie.domain and cookie.value}