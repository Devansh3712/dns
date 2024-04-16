import struct
from io import BytesIO


#  +---+---+---+---+---+---+---+---+---+---+----+
#  | a | b | c | . | d | e | . | c | o | m | \0 |
#  +---+---+---+---+---+---+---+---+---+---+----+
#
#  +---+---+---+---+---+---+---+---+---+---+---+----+
#  | 3 | a | b | c | 2 | d | e | 3 | c | o | m | \0 |
#  +---+---+---+---+---+---+---+---+---+---+---+----+
def encode_name(qname: bytes) -> bytes:
    encoded = bytes()
    for label in qname.split(b"."):
        encoded += bytes([len(label)]) + label
    return encoded + b"\x00"


def decode_compressed_name(length: int, reader: BytesIO) -> bytes:
    pointer_bytes = bytes([length & 0x3F]) + reader.read(1)
    (pointer,) = struct.unpack("!H", pointer_bytes)
    current_position = reader.tell()
    reader.seek(pointer)
    result = decode_name(reader)
    reader.seek(current_position)
    return result


def decode_name(reader: BytesIO) -> bytes:
    parts = []
    while (length := reader.read(1)[0]) != 0:
        if length & 0xC0:
            parts.append(decode_compressed_name(length, reader))
            break
        parts.append(reader.read(length))
    return b".".join(parts)
