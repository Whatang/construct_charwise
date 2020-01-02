from construct.lib.py3compat import *
from typing import (
    Any,
    Hashable,
    List,
    KeysView,
    ValuesView,
    ItemsView,
    Iterator,
    Optional as TypingOptional,
    Mapping as TypingMapping,
)
import re

globalPrintFullStrings: bool
globalPrintFalseFlags: bool
globalPrintPrivateEntries: bool

def setGlobalPrintFullStrings(enabled: bool = ...) -> None: ...
def setGlobalPrintFalseFlags(enabled: bool = ...) -> None: ...
def setGlobalPrintPrivateEntries(enabled: bool = ...) -> None: ...
def recursion_lock(retval: str = ..., lock_name: str = ...): ...

class Container(dict):
    __slots__: Any = ...
    def __getattr__(self, name: str): ...
    def __setattr__(self, name: str, value: Any): ...
    def __delattr__(self, name: str): ...
    def __setitem__(self, key: Hashable, value: Any) -> None: ...
    def __delitem__(self, key: Hashable) -> None: ...
    __keys_order__: List[Any] = ...
    def __init__(self, *args: Any, **entrieskw: Any) -> None: ...
    def __call__(self, **entrieskw: Any): ...
    def keys(self) -> KeysView: ...
    def values(self) -> ValuesView: ...
    def items(self) -> ItemsView: ...
    def __iter__(self) -> Iterator[Any]: ...
    def clear(self) -> None: ...
    def pop(self, key: Any, default=TypingOptional[Any]): ...  # type: ignopre
    def popitem(self): ...
    def update(self, seqordict: Union[TypingMapping, List[Tuple[Any, Any]]]) -> None: ...  # type: ignore
    def __getstate__(self): ...
    def __setstate__(self, state: Any) -> None: ...
    def copy(self): ...
    def __dir__(self): ...
    def __eq__(self, other: Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def _search(self, compiled_pattern: re.Pattern, search_all: bool) -> List[Any]: ...
    def search(self, pattern: str) -> List[Any]: ...
    def search_all(self, pattern: str) -> List[Any]: ...

class ListContainer(list):
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def _search(self, compiled_pattern: re.Pattern, search_all: bool) -> List[Any]: ...
    def search(self, pattern: str) -> List[Any]: ...
    def search_all(self, pattern: str) -> List[Any]: ...
