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
    match browser:
        case Browser.ANY:
            cookies = browser_cookie3.load()
        case Browser.FIREFOX:
            cookies = browser_cookie3.firefox()
        case Browser.CHROME:
            cookies = browser_cookie3.chrome()
        case Browser.EDGE:
            cookies = browser_cookie3.edge()
        case Browser.SAFARI:
            cookies = browser_cookie3.safari()
        case Browser.CHROMIUM:
            cookies = browser_cookie3.chromium()
        case Browser.VIVALDI:
            cookies = browser_cookie3.vivaldi()
        case Browser.EDGE_DEV:
            raise ValueError("EDGE_DEV is not supported anymore.")
        case _:
            assert_never(browser)
    assert isinstance(cookies, CookieJar)
    return {cookie.name: cookie.value for cookie in cookies if "scratch.mit.edu" in cookie.domain and cookie.value}