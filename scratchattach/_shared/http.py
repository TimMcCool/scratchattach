from __future__ import annotations
from dataclasses import dataclass
from typing import TypeAlias, TypeVar, Protocol, runtime_checkable, Any
from collections.abc import Iterable

_CT_co = TypeVar("_CT_co", covariant=True)

_KT_co = TypeVar("_KT_co", covariant=True)
_VT_co = TypeVar("_VT_co", covariant=True)


@runtime_checkable
class SupportsReadAll(Protocol[_CT_co]):
    def read(self) -> _CT_co: ...


@runtime_checkable
class SupportsItems(Protocol[_KT_co, _VT_co]):
    def items(self) -> Iterable[tuple[_KT_co, _VT_co]]: ...


_ParamsValue: TypeAlias = (
    str | int | float | Iterable[str | int | float]
)


@runtime_checkable
class HTTPFile(Protocol):
    def get_content(self) -> bytes: ...


@dataclass
class BufferHTTPFile(HTTPFile):
    buffer: SupportsReadAll[bytes]

    def get_content(self) -> bytes:
        return self.buffer.read()


_FilesValue: TypeAlias = HTTPFile | bytes

_JsonEmptySentinel = object()

class HTTPOptions:
    __slots__ = ["params"]
    params: (
        Iterable[tuple[str, _ParamsValue]]
        | SupportsItems[str, _ParamsValue]
        | str
        | None
    ) = None
    content: str | bytes | None = None
    data: Iterable[tuple[str, Any]] | SupportsItems[str, Any] | None = None
    files: Iterable[tuple[str, _FilesValue]] | SupportsItems[str, _FilesValue] | None = None
    json: Any = _JsonEmptySentinel
    headers: Iterable[tuple[str, str]] | SupportsItems[str, str] | None = None
    cookies: Iterable[tuple[str, str]] | SupportsItems[str, str] | None = None
