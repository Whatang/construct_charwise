from construct_charwise import FixedLengthCharacterString
from construct import Struct, this, Byte


field_reader = FixedLengthCharacterString.from_encoding("ascii", 4)
print(field_reader.parse(b"abcd"))

FixedLengthCharacterString.from_encoding("ascii", this.length)

field_reader2 = Struct(
    "length" / Byte,
    "data" / FixedLengthCharacterString.from_encoding("ascii", this.length),
)
print(field_reader2.parse(b"\x02abcd"))
