from construct import Construct, Path, CodeGen, Subconstruct
from construct.lib import Container
from typing import Any, Optional as TypingOptional, IO, Callable

class Probe(Construct):
    flagbuildnone: bool = ...
    into: TypingOptional[Callable[[Container], Container]] = ...
    lookahead: int = ...
    def __init__(
        self,
        into: TypingOptional[Callable[[Container], Container]] = ...,
        lookahead: TypingOptional[int] = ...,
    ) -> None: ...
    def _parse(self, stream: IO, context: Container, path: Path) -> None: ...
    def _build(self, obj: Any, stream: Any, context: Any, path: Any) -> None: ...
    def _sizeof(self, context: Container, path: Path) -> int: ...
    def _emitparse(self, code: CodeGen) -> str: ...
    def printout(self, stream: IO, context: Container, path: Path) -> None: ...

class Debugger(Subconstruct):
    retval: Any = ...
    def _parse(self, stream: IO, context: Container, path: Path): ...
    def _build(self, obj: Any, stream: Any, context: Any, path: Any): ...
    def _sizeof(self, context: Container, path: Path) -> int: ...
    def _emitparse(self, code: CodeGen) -> str: ...
    def handle_exc(self, path: Path, msg: TypingOptional[str] = ...) -> None: ...
