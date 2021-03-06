import builtins

from typing import (
    Any,
    Tuple,
    Type,
    Mapping as TypingMapping,
    Iterable,
    Union as TypingUnion,
)

PY: bool
PY2: bool
PY3: bool
PYPY: bool
supportsnumpy: bool
supportsksyexport: bool
supportsintenum: bool
supportsintflag: bool
supportskwordered: bool
stringtypes: Tuple[Type]
integertypes: Tuple[Type]
unicodestringtype = str
bytestringtype = bytes
INT2BYTE_CACHE: TypingMapping[int, bytes]

def int2byte(character: Any): ...
def byte2int(character: Any): ...
def str2bytes(string: str) -> bytes: ...
def bytes2str(string: bytes) -> str: ...
def str2unicode(string: str) -> str: ...
def unicode2str(string: str) -> str: ...

ITERATEBYTES_CACHE: TypingMapping[int, bytes]

def iteratebytes(data: bytes) -> Iterable[bytes]: ...
def iterateints(data: bytes) -> Iterable[int]: ...
def reprstring(data: TypingUnion[bytes, str]) -> str: ...
def trimstring(data: TypingUnion[bytes, str]) -> str: ...

bytes = builtins.bytes

def integers2bytes(ints: Iterable[int]) -> bytes: ...
def bytes2integers(data: bytes) -> Iterable[int]: ...
