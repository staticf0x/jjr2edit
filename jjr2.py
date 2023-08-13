import os
import struct
from argparse import ArgumentParser
from dataclasses import dataclass

from devtools import debug


def read_string_length(file) -> int:
    return struct.unpack("b", f.read(1))[0]


def read_string(file, length: int = 0) -> str:
    if not length:
        length = read_string_length(file)

    return struct.unpack(f"{length}s", f.read(length))[0].decode("Windows-1252")


def read_int(file) -> int:
    return struct.unpack("i", f.read(4))[0]


def read_short(file) -> int:
    return struct.unpack("h", f.read(2))[0]


def read_byte(file) -> int:
    return struct.unpack("b", f.read(1))[0]


def skip_bytes(file, bytes: int) -> int:
    file.seek(bytes, os.SEEK_CUR)


@dataclass
class Section:
    name: str
    length: int

    @staticmethod
    def read_section(f):
        return Section(read_string(f, 4), read_int(f))


parser = ArgumentParser()
parser.add_argument("path")

args = parser.parse_args()

with open(args.path, "rb") as f:
    # DDCF
    section = Section.read_section(f)
    debug(section)

    # EDIT
    section = Section.read_section(f)
    debug(section)

    start = f.tell()
    debug(start=start)
    debug(section_length=section.length)
    debug(focused_layer=read_byte(f))

    debug(image_filename=read_string(f))
    debug(number_of_tiles=read_int(f))
    skip_bytes(f, 1)  # Unknown byte

    while f.tell() < section.length + start - 1:  # -1 for the section divider
        debug(layer_name=read_string(f))

    if section.length + start - f.tell() == 1:
        skip_bytes(f, 1)

    # EDI2
    section = Section.read_section(f)
    debug(section)

    skip_bytes(f, section.length)  # Skip to the end of the section
    print(f.tell())

    # LINF
    section = Section.read_section(f)
    debug(chunk_version=read_short(f))
    debug(level_name=read_string(f))
    skip_bytes(f, 1)
    debug(music_file=read_string(f))
    debug(next_level=read_string(f))
