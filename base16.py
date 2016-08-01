#! /usr/bin/env python3

import sys
import getopt
import pprint

base16 = '0123456789ABCDEF'

# always one byte
def b16enc_block(block):
    e_block = ""

    e_block = e_block + base16[((block[0] & 0xF0) >> 4)]
    e_block = e_block + base16[(block[0] & 0x0F)]

    return e_block

# always two characters
def b16dec_block(e_block):
    return bytes([ (base16.index(e_block[0]) << 4) | base16.index(e_block[1]) ])

def main():
    e_block = b16enc_block(b'\xab')

    print(e_block)

    block = b16dec_block('64')

    print(block)
    pass

if __name__ == '__main__':
    main()
