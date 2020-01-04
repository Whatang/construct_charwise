from typing import Any, Optional as TypingOptional, IO, Callable

class RestreamedBytesIO:
    substream: IO = ...
    encoder: Callable[[bytes], bytes] = ...
    encoderunit: Any = ...
    decoder: Callable[[bytes], bytes] = ...
    decoderunit: Any = ...
    rbuffer: bytes = ...
    wbuffer: bytes = ...
    sincereadwritten: int = ...
    def __init__(
        self,
        substream: IO,
        decoder: Callable[[bytes], bytes],
        decoderunit: int,
        encoder: Callable[[bytes], bytes],
        encoderunit: int,
    ) -> None: ...
    def read(self, count: TypingOptional[int] = ...) -> bytes: ...
    def write(self, data: bytes) -> int: ...
    def close(self) -> None: ...
    def seek(self, at: Any, whence: int = ...) -> int: ...
    def seekable(self) -> bool: ...
    def tell(self) -> int: ...
    def tellable(self) -> bool: ...

class RebufferedBytesIO:
    substream: IO = ...
    offset: int = ...
    rwbuffer: bytes = ...
    moved: int = ...
    tailcutoff: TypingOptional[int] = ...
    def __init__(
        self, substream: IO, tailcutoff: TypingOptional[int] = ...
    ) -> None: ...
    def read(self, count: TypingOptional[int] = ...) -> bytes: ...
    def write(self, data: bytes) -> int: ...
    def seek(self, at: Any, whence: int = ...) -> int: ...
    def seekable(self) -> bool: ...
    def tell(self) -> int: ...
    def tellable(self) -> bool: ...
    def cachedfrom(self) -> int: ...
    def cachedto(self) -> int: ...
