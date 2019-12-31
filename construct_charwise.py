from __future__ import annotations
from construct import Construct, SizeofError, StreamError
from typing import Dict, Iterable, Union, IO, Callable, Any, Container, TypeVar
import attr

# Base construct for reading 1 character at a time from a byetstream containing
# encoded characters.

# Use composition to separate out different parsing strategies and character
# sizes, without binding into an inheritance hierarchy.

# Use attrs to only allow creation of a fully formed Character construct. Any
# work done to build the component parts must be done beforehand, such as by
# the `get` class method.

ContextType = Container
PathType = Any
ParserFuncType = Callable[["Character", IO, ContextType, PathType], str]
SizeOfFuncType = Callable[["Character", ContextType, PathType], int]


@attr.s
class Character(Construct):
    encoding_name: str = attr.ib()
    parse_func: ParserFuncType = attr.ib()
    sizeof_func: SizeOfFuncType = attr.ib()

    _characters_by_encoding: Dict[str, Character] = {}

    def __attrs_post_init__(self):
        super(Character, self).__init__()

    def decode_bytes(self, bytevals: bytes) -> str:
        return str(bytevals, self.encoding_name)

    def encode_str(self, string: str) -> bytes:
        return bytes(string, self.encoding_name)

    def _parse(self, stream: IO, context: ContextType, path: PathType) -> str:
        return self.parse_func(self, stream, context, path)

    def _build(self, obj, stream: IO, context: ContextType, path: PathType) -> bytes:
        data = b""
        if len(obj) > 0:
            data = bytes(obj[0], self.encoding_name)
            stream.write(data)
        return data

    def _sizeof(self, context: ContextType, path: PathType) -> int:
        return self.sizeof_func(self, context, path)

    @classmethod
    def _name_variants(cls, name: str) -> Iterable[str]:
        name = name.lower()
        yield name
        name = name.replace("_", "-")
        yield name
        yield name.replace("-", "_")
        if name.count("-") == 1:
            yield name.replace("_", "-").replace("-", "")
        if name.count("-") == 2:
            index = name.rfind("-")
            name1 = name[:index] + name[index + 1 :]
            yield name1
            yield name1.replace("-", "_")

    @classmethod
    def add_encoding(
        cls,
        encoding_names: Union[str, Iterable[str]],
        parse_func: ParserFuncType,
        sizeof_func: SizeOfFuncType,
    ) -> None:
        if isinstance(encoding_names, str):
            encoding_names = [encoding_names]
        names = set()
        for encoding_name in encoding_names:
            for name in cls._name_variants(encoding_name):
                names.add(name)
        for name in names:
            if name not in cls._characters_by_encoding:
                cls._characters_by_encoding[name] = Character(
                    name, parse_func, sizeof_func
                )

    @classmethod
    def get(cls, encoding: str) -> Character:
        return cls._characters_by_encoding[encoding]


# Parsing functions to be used by Characters


def _parse_utf8(
    character: Character, stream: IO, context: ContextType, path: PathType
) -> str:
    first = stream.read(1)
    data = first
    first = first[0]
    if first & 0x80 != 0:
        if first & 0xE0 == 0xC0:
            extra = 1
        elif first & 0xF0 == 0xE0:
            extra = 2
        elif first & 0xF8 == 0xF0:
            extra = 3
        else:
            # This is a decoding error: it's not valid UTF8
            extra = 0
        data += stream.read(extra)
    return character.decode_bytes(data)


def _parse_fixed_width(
    character: Character, stream: IO, context: ContextType, path
) -> str:
    return character.decode_bytes(stream.read(character.sizeof()))


# Sizeof functions


def _sizeof_error(character: Character, context: ContextType, path: PathType):
    raise SizeofError()


def _fixed_sizeof(width: int) -> SizeOfFuncType:
    def fixed_width(character: Character, context: ContextType, path: PathType) -> int:
        return width

    return fixed_width


# Define the known encodings

Character.add_encoding(["ascii"], _parse_fixed_width, _fixed_sizeof(1))
Character.add_encoding(["utf-8", "u8"], _parse_utf8, _sizeof_error)
Character.add_encoding(
    ["u16", "utf-16", "utf-16-le", "utf-16-be"], _parse_fixed_width, _fixed_sizeof(2)
)
Character.add_encoding(
    ["u32", "utf-32", "utf-32-le", "utf-32-be"], _parse_fixed_width, _fixed_sizeof(4)
)

# Construct for building strings of characters from encoded byte streams

# This class just implements an algorithm skeleton for parsing strings by
# character, but with key steps of the algorithm parametrized. Functions
# implementing these steps are passed in as arguments, i.e. composition
# rather than inheritance.

_T = TypeVar("_T")
ContextVariable = Union[_T, Callable[[ContextType], _T]]

CharGetterFuncType = Callable[["CharacterString", IO, ContextType, PathType], str]
KeepGoingFuncType = Callable[["CharacterString", str, ContextType], bool]
PostProcessFuncType = Callable[["CharacterString", str, ContextType], str]
BuildFuncType = Callable[["CharacterString", Any, IO, ContextType, PathType], bytes]


@attr.s
class CharacterString(Construct):
    character: Character = attr.ib()
    _char_getter: CharGetterFuncType = attr.ib()
    _keep_going_checker: KeepGoingFuncType = attr.ib()
    _post_processor: PostProcessFuncType = attr.ib()
    _builder: BuildFuncType = attr.ib()

    class StopHere(RuntimeError):
        pass

    def __attrs_post_init__(self):
        super(CharacterString, self).__init__()

    def _parse(self, stream: IO, context: ContextType, path: PathType) -> str:
        data = ""
        try:
            while self._keep_going_checker(self, data, context):
                data += self._char_getter(self, stream, context, path)
        except self.StopHere:
            pass
        if len(data) == 0:
            # We have to put this in to stop an infinite loop
            # when matching the empty string
            raise StreamError()
        return self._post_processor(self, data, context)

    def _build(self, obj, stream: IO, context: ContextType, path: PathType) -> bytes:
        return self._builder(self, obj, stream, context, path)

    def _sizeof(self, context: ContextType, path: PathType) -> int:
        # TODO: implement sizeof capability
        raise NotImplementedError


@attr.s
class CharStringFactory:
    ch_str_maker: Callable[..., CharacterString] = attr.ib()

    def __call__(self, character: Character, *args, **kwargs) -> CharacterString:
        return self.ch_str_maker(character, *args, **kwargs)

    def from_encoding(self, encoding: str, *args, **kwargs) -> CharacterString:
        character = Character.get(encoding)
        return self(character, *args, **kwargs)


# An instantiation of CharacterString which parses a fixed number of characters.


def make_fixed_length_char_string(
    character: Character, length: ContextVariable[int]
) -> CharacterString:
    return CharacterString(
        character,
        char_getter=_simple_get_next_char,
        keep_going_checker=_fixed_length_checker(length),
        post_processor=_do_nothing_post_processor,
        builder=_fixed_length_builder(length),
    )


FixedLengthCharacterString = CharStringFactory(make_fixed_length_char_string)


# The methods which implement FixedLengthCharacterString: we
# may be able to re-use these for some other type of CharacterString
# if there is an overlap in functionality.


def _simple_get_next_char(
    char_str: CharacterString, stream: IO, context: ContextType, path: PathType
) -> str:
    return char_str.character._parsereport(stream, context, path)


def _fixed_length_checker(length: ContextVariable[int]) -> KeepGoingFuncType:
    def has_reached_fixed_length(
        char_str: CharacterString, data: str, context: ContextType
    ) -> bool:
        length_ = length(context) if callable(length) else length
        return len(data) < length_

    return has_reached_fixed_length


def _do_nothing_post_processor(
    char_str: CharacterString, data: str, context: ContextType
) -> str:
    return data


def _fixed_length_builder(length: ContextVariable[int]) -> BuildFuncType:
    def _fixed_length_string_builder(
        cstr: CharacterString, obj, stream: IO, context: ContextType, path: PathType
    ) -> bytes:
        # TODO: what's the right behavior here?
        raise NotImplementedError()

    return _fixed_length_string_builder


# An instantiation of CharacterString which parses characters until a specified
# terminating string is encountered, or the stream ends.


def make_terminated_character_string(
    character: Character,
    term: ContextVariable[str] = "\n",
    consume: ContextVariable[bool] = True,
    require: ContextVariable[bool] = True,
) -> CharacterString:
    return CharacterString(
        character,
        char_getter=_get_next_char_or_maybe_error(require),
        keep_going_checker=_terminating_checker(term),
        post_processor=_terminating_post_processor(term, consume),
        builder=_terminating_string_builder(term),
    )


TerminatedCharacterString = CharStringFactory(make_terminated_character_string)


def _get_next_char_or_maybe_error(require: ContextVariable[bool]) -> CharGetterFuncType:
    def _get_next_char(
        char_str: CharacterString, stream: IO, context: ContextType, path: PathType
    ):
        try:
            return char_str.character._parsereport(stream, context, path)
        except StreamError:
            require_ = require(context) if callable(require) else require
            if require_:
                raise
            else:
                raise char_str.StopHere()

    return _get_next_char


def _terminating_checker(term: ContextVariable[str]) -> KeepGoingFuncType:
    def terminating_string_check(
        char_str: CharacterString, data: str, context: ContextType
    ) -> bool:
        term_ = term(context) if callable(term) else term
        return len(data) < len(term_) or data[-len(term_) :] != term

    return terminating_string_check


def _terminating_post_processor(
    term: ContextVariable[str], consume: ContextVariable[bool]
) -> PostProcessFuncType:
    def terminating_post_process(
        char_str: CharacterString, data: str, context: ContextType
    ) -> str:
        term_ = term(context) if callable(term) else term
        consume_ = consume(context) if callable(consume) else consume
        if consume_ and len(data) >= len(term_) and data.endswith(term_):
            data = data[: -len(term_)]
        return data

    return terminating_post_process


def _terminating_string_builder(term: ContextVariable[str]) -> BuildFuncType:
    def _build_terminated_string(
        char_str: CharacterString, obj, stream: IO, context: ContextType, path: PathType
    ) -> bytes:
        term_ = term(context) if callable(term) else term
        data = b""
        for char in obj + term_:
            data += char_str.character._build(char, stream, context, path)
        return data

    return _build_terminated_string


def WindowsCharacterLine(encoding: str, consume=True, require=False) -> CharacterString:
    return TerminatedCharacterString.from_encoding(
        encoding=encoding, term="\r\n", consume=consume, require=require
    )


def LinuxCharacterLine(encoding: str, consume=True, require=False) -> CharacterString:
    return TerminatedCharacterString.from_encoding(
        encoding=encoding, term="\n", consume=consume, require=require
    )
