from __future__ import annotations
from dataclasses import dataclass
from typing import TypeAlias, TypeVar, Protocol, runtime_checkable, Any, BinaryIO, Self, Final
from collections.abc import Iterable
from enum import Enum, auto

_CT_co = TypeVar("_CT_co", covariant=True)

_KT_co = TypeVar("_KT_co", covariant=True)
_VT_co = TypeVar("_VT_co", covariant=True)


@runtime_checkable
class SupportsItems(Protocol[_KT_co, _VT_co]):
    def items(self) -> Iterable[tuple[_KT_co, _VT_co]]: ...


_ParamsValue: TypeAlias = str | int | float | Iterable[str | int | float] | None

_FilesValue: TypeAlias = BinaryIO | bytes

_JsonEmptySentinel = object()


def options() -> HTTPOptionsBuilder:
    return HTTPOptionsBuilder()


class HTTPOptionsBuilder:
    __slots__ = ["value"]
    value: HTTPOptions

    def __init__(self):
        self.value = HTTPOptions()

    def params(
        self,
        value: Iterable[tuple[str, _ParamsValue]] | SupportsItems[str, _ParamsValue] | str | None,
    ) -> Self:
        self.value.params = value
        return self

    def content(self, value: str | bytes | None) -> Self:
        self.value.content = value
        return self

    def data(self, value: Iterable[tuple[str, Any]] | SupportsItems[str, Any] | None) -> Self:
        self.value.data = value
        return self

    def files(
        self, value: Iterable[tuple[str, _FilesValue]] | SupportsItems[str, _FilesValue] | None
    ) -> Self:
        self.value.files = value
        return self

    def json(self, value: Any) -> Self:
        self.value.json = value
        return self

    def headers(self, value: Iterable[tuple[str, str]] | SupportsItems[str, str] | None) -> Self:
        self.value.headers = value
        return self

    def disregard_default_headers(self, value: bool = True) -> Self:
        self.value.disregard_default_headers = value
        return self

    def cookies(self, value: Iterable[tuple[str, str]] | SupportsItems[str, str] | None) -> Self:
        self.value.cookies = value
        return self

    def disregard_default_cookies(self, value: bool = True) -> Self:
        self.value.disregard_default_cookies = value
        return self

    def timeout(self, value: int | float | None) -> Self:
        self.value.timeout = value
        return self


class HTTPOptions:
    params: Iterable[tuple[str, _ParamsValue]] | SupportsItems[str, _ParamsValue] | str | None = (
        None
    )
    content: str | bytes | None = None
    data: Iterable[tuple[str, Any]] | SupportsItems[str, Any] | None = None
    files: Iterable[tuple[str, _FilesValue]] | SupportsItems[str, _FilesValue] | None = None
    json: Any = _JsonEmptySentinel
    headers: Iterable[tuple[str, str]] | SupportsItems[str, str] | None = None
    disregard_default_headers: bool = False
    cookies: Iterable[tuple[str, str]] | SupportsItems[str, str] | None = None
    disregard_default_cookies: bool = False
    timeout: int | float | None = None


class HTTPMethod(Enum):
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()


_EMPTY_OPTIONS: Final = HTTPOptions()

class JSONError(Exception):
    pass
