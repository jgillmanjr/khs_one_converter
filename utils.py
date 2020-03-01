"""
Utility functions for the ONE converter
"""

def convert_magic(input: str):
    """
    Do some bitwise magic on a string. I'm guessing this is for file type magic numbers
    :param input:
    :return:
    """
    if len(input) != 4:
        raise Exception('Ooops. This should probably have 4 characters...')
    converted_magic = (ord(input[0]) << 24) | (ord(input[1]) << 16) | (ord(input[2]) << 8) | ord(input[3])
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


def read_b_uint(bytes_input: bytes, big_endian: bool = True) -> int:
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
    return int.from_bytes(bytes_input, endian, signed=False)
