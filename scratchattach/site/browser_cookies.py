from typing import Optional, TYPE_CHECKING
from typing_extensions import assert_never
from http.cookiejar import CookieJar
from enum import Enum, auto
browsercookie_err = None
try:
    if TYPE_CHECKING:
        from . import browser_cookie3_stub as browser_cookie3
    else:
        import browser_cookie3
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
    VIVALDI = auto()
    EDGE_DEV = auto()

    
FIREFOX = Browser.FIREFOX
CHROME = Browser.CHROME
EDGE = Browser.EDGE
SAFARI = Browser.SAFARI
CHROMIUM = Browser.CHROMIUM
VIVALDI = Browser.VIVALDI
ANY = Browser.ANY
EDGE_DEV = Browser.EDGE_DEV

def cookies_from_browser(browser : Browser = ANY) -> dict[str, str]:
    """
    Import cookies from browser to login
    """
    if not browser_cookie3:
        raise browsercookie_err or ModuleNotFoundError()
    cookies : Optional[CookieJar] = None
    if browser is Browser.ANY:
        cookies = browser_cookie3.load()
    elif browser is Browser.FIREFOX:
        cookies = browser_cookie3.firefox()
    elif browser is Browser.CHROME:
        cookies = browser_cookie3.chrome()
    elif browser is Browser.EDGE:
        cookies = browser_cookie3.edge()
    elif browser is Browser.SAFARI:
        cookies = browser_cookie3.safari()
    elif browser is Browser.CHROMIUM:
        cookies = browser_cookie3.chromium()
    elif browser is Browser.VIVALDI:
        cookies = browser_cookie3.vivaldi()
    elif browser is Browser.EDGE_DEV:
        raise ValueError("EDGE_DEV is not supported anymore.")
    else:
        assert_never(browser)
    assert isinstance(cookies, CookieJar)
    return {cookie.name: cookie.value for cookie in cookies if "scratch.mit.edu" in cookie.domain and cookie.value}