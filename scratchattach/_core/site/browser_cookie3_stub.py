# browser_cookie3.pyi

import http.cookiejar
from typing import Optional

def chrome(cookie_file: Optional[str] = None, key_file: Optional[str] = None) -> http.cookiejar.CookieJar: return NotImplemented
def chromium(cookie_file: Optional[str] = None, key_file: Optional[str] = None) -> http.cookiejar.CookieJar: return NotImplemented
def firefox(cookie_file: Optional[str] = None, key_file: Optional[str] = None) -> http.cookiejar.CookieJar: return NotImplemented
def opera(cookie_file: Optional[str] = None, key_file: Optional[str] = None) -> http.cookiejar.CookieJar: return NotImplemented
def edge(cookie_file: Optional[str] = None, key_file: Optional[str] = None) -> http.cookiejar.CookieJar: return NotImplemented
def brave(cookie_file: Optional[str] = None, key_file: Optional[str] = None) -> http.cookiejar.CookieJar: return NotImplemented
def vivaldi(cookie_file: Optional[str] = None, key_file: Optional[str] = None) -> http.cookiejar.CookieJar: return NotImplemented
def safari(cookie_file: Optional[str] = None, key_file: Optional[str] = None) -> http.cookiejar.CookieJar: return NotImplemented
def lynx(cookie_file: Optional[str] = None, key_file: Optional[str] = None) -> http.cookiejar.CookieJar: return NotImplemented
def w3m(cookie_file: Optional[str] = None, key_file: Optional[str] = None) -> http.cookiejar.CookieJar: return NotImplemented

def load() -> http.cookiejar.CookieJar: return NotImplemented
