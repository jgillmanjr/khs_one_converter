"""
Utility functions for the ONE converter
"""
from typing import Union

CURRENT_VERSION = 1014


def convert_magic(st_input: str) -> int:
    """
    Do some bitwise magic on a string. I'm guessing this is for file type magic numbers
    :param st_input:
    :return:
    """
    if len(st_input) != 4:
        raise Exception('Ooops. This should probably have 4 characters...')
    converted_magic = (ord(st_input[0]) << 24) | (ord(st_input[1]) << 16) | (ord(st_input[2]) << 8) | ord(st_input[3])
    return converted_magic


def write_uint_b(int_input: int, big_endian: bool = True) -> bytes:
    """
    Dump 4 bytes from an int.
    Big endian by default.
    Basically mimicking writeUnsignedInt from ActionScript
    :param int_input:
    :param big_endian:
    :return:
    """
    if big_endian:
        endian = 'big'
    else:
        endian = 'little'
    return int_input.to_bytes(4, endian, signed=False)


def read_b_uint(bytes_input: Union[bytes, bytearray], big_endian: bool = True) -> int:
    """
    Get an int from 4 bytes
    Big endian by default
    Basically mimicking readUnsignedInt
    :param bytes_input:
    :param big_endian:
    :return:
    """
    if big_endian:
        endian = 'big'
    else:
        endian = 'little'

    if isinstance(bytes_input, bytearray):
        rinput = range_pop(bytes_input, 0, 4)  # Makes it easier this way. I think.
    else:
        rinput = bytes_input
    return int.from_bytes(rinput, endian, signed=False)


def range_pop(ltype, start: int, stop: int) -> Union[list, bytearray]:
    """
    Emulate popping an arbitrary range
    :param ltype:
    :param start:
    :param stop:
    :return:
    """

    s = slice(start, stop, 1)

    returned_slice = ltype[s]
    del ltype[s]
    return returned_slice
