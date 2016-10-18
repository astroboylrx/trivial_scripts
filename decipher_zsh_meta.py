#!/usr/bin/env python3

""" In zsh history file, some functional bytes are escaped with meta
    character. As of it, non-ascii texts in history file are sometimes
    undecipherable.

    According to `init.c' of zsh, followings are meta characters.

    - 0x00, 0x83(Meta), 0x84(Pound)-0x9d(Nularg), 0xa0(Marker)

    For these bytes, 0x83(Meta) is preceded and target byte is `xor'ed
    with 0x20.

    This script takes one argument and deciphers those meta characters 
    back to normal utf-8 bytes.
"""

import sys


def decipher_meta_char(immu_bytes):
    """Decipher the leading byte"""
    bytearr = bytearray(immu_bytes)
    bytearr[0] ^= 32 # equal to 0x20
    return bytes(bytearr)


if __name__ == "__main__":
    # obtain stdin and look for the characteristic byte --> 0x83
    content = sys.stdin.buffer.read().split(bytes([0x83]))
    if len(content) > 1:
        # convert meta characters back to normal
        new_content = [content[0]] + [decipher_meta_char(x) for x in content[1:]]
        sys.stdout.buffer.write(b"".join(new_content))
    else:
        sys.stdout.buffer.write(content[0])