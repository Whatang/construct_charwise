from construct import *
import attr

# Base construct for reading 1 character at a time from a byetstream containing
# encoded characters.

# Use composition to separate out different parsing strategies and character sizes,
# without binding into an inheritance hierarchy.

# Use attrs to only allow creation of a fully formed Character construct. Any work
# done to build 

@attr.s
class Character(Construct):
    encoding_name = attr.ib()
    parse_func = attr.ib()
    sizeof_func = attr.ib()

    _characters_by_encoding = {}

    def __attrs_post_init__(self):
        super(Character, self).__init__()

    def decode_bytes(self, bytevals):
        return str(bytevals, self.encoding_name)

    def encode_str(self, string):
        return bytes(string, self.encoding_name)

    def _parse(self, stream, context, path):
        return self.parse_func(self, stream, context, path)

    def _build(self, obj, stream, context, path):
        data = b""
        if len(obj) > 0:
            data = bytes(obj[0], self.encoding_name)
            stream.write(data)
        return data

    def _sizeof(self, context, path):
        return self.sizeof_func(self, context, path)

    @classmethod
    def _name_variants(cls, name):
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
    def add_encoding(cls, encoding_names, parse_func, sizeof_func):
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
    def get(cls, encoding):
        return cls._characters_by_encoding[encoding]

# Parsing functions to be used by Characters

def _parse_utf8(character: Character, stream, context, path):
    first = stream.read(stream, 1)
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


def _parse_fixed_width(character: Character, stream, context, path):
    return character.decode_bytes(stream.read(character.sizeof()))

# Sizeof functions

def _sizeof_error(character: Character, context, path):
    raise SizeofError()


def _fixed_sizeof(width):
    return lambda character: Character, *args, **kwargs: width

# Define the known encodings

Character.add_encoding(["utf-8", "u8"], _parse_utf8, _sizeof_error)
Character.add_encoding(
    ["u16", "utf-16", "utf-16-le", "utf-16-be"], _parse_fixed_width, _fixed_sizeof(2)
)
Character.add_encoding(
    ["u32", "utf-32", "utf-32-le", "utf-32-be"], _parse_fixed_width, _fixed_sizeof(4)
)

# Base construct for building strings of characters from encoded byte streams

@attr.s
class CharacterString(Construct):
    character: Character = attr.ib()
    _stop = attr.ib(init=False, default=False)

    def __attrs_post_init__(self):
        super(CharacterString, self).__init__()

    @classmethod
    def from_encoding(cls, encoding="utf8"):
        return cls(Character.get(encoding))

    def _parse(self, stream, context, path):
        data = ""
        self._stop = False
        while not self._stop and self._keep_going(data):
            data += self._get_next_char(stream, context, path)
        if len(data) == 0:
            # We have to put this in to stop an infinite loop
            # when matching the empty string
            raise StreamError()
        return self._post_process(data)

    def _keep_going(self, data):
        raise NotImplementedError()

    def _get_next_char(self, stream, context, path):
        return self.character._parsereport(stream, context, path)

    def _post_process(self, data):
        return data

    def _build(self, obj, stream, context, path):
        raise NotImplementedError()


@attr.s
class FixedLengthCharacterString(CharacterString):
    _length = attr.ib()

    @classmethod
    def from_encoding(cls, encoding, length):
        return cls(Character.get(encoding), length)

    def _keep_going(self, data):
        return len(data) < self._length


@attr.s
class TerminatedCharacterString(CharacterString):
    _term = attr.ib(default="\n")
    _consume = attr.ib(default=True)
    _require = attr.ib(default=True)

    @classmethod
    def from_encoding(cls, encoding="utf8", term="\n", consume=True, require=True):
        return cls(Character.get(encoding), term, consume, require)

    def _keep_going(self, data):
        return len(data) < len(self._term) or data[-len(self._term) :] != self._term

    def _get_next_char(self, stream, context, path):
        try:
            return self.character._parsereport(stream, context, path)
        except StreamError:
            if self._require:
                raise
            else:
                self._stop = True
                return ""

    def _post_process(self, data):
        if self._consume and len(data) > len(self._term):
            data = data[: -len(self._term)]
        return data

    def _build(self, obj, stream, context, path):
        data = b""
        for char in obj + self._term:
            data += self.character._build(char, stream, context, path)
        return data


WindowsCharacterLine = lambda encoding, consume=True, require=False: TerminatedCharacterString.from_encoding(
    encoding=encoding, term="\r\n", consume=consume, require=require
)
LinuxCharacterLine = lambda encoding, consume=True, require=False: TerminatedCharacterString.from_encoding(
    encoding=encoding, term="\n", consume=consume, require=require
)

CharacterLine = lambda encoding, consume=True, require=False: Select(
    WindowsCharacterLine(encoding=encoding, consume=consume, require=require),
    LinuxCharacterLine(encoding=encoding, consume=consume, require=require),
)

