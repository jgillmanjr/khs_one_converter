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
        raise Exception('Ooops. This should probably 4 characters...')
    converted_magic = (ord(input[0]) << 24) | (ord(input[1]) << 16) | (ord(input[2]) << 8) | ord(input[3])
    return converted_magic

def byte_dump(input: int) -> bytes:
    """
    Dump bytes from an int.
    Big endian
    :param input:
    :return:
    """
    byte_length = (input.bit_length() + 7) // 8
    return input.to_bytes(byte_length, 'big')
