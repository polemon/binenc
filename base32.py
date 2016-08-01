#!/usr/bin/env python3

import os
import sys
from stat import *

b32dict = "0123456789ABCDEFGHIJKLMNOPQRSTUV"
pad_c = '='
padding = [0, 6, 4, 3, 1, 0]


def b32encode_block(block):
    val = list()

    for i in range(len(block), 5):
        block += b'\x00'

    val.insert(0, block[4] & b'\x1f'[0])
    val.insert(0, ( (block[3] << 3) | (block[4] >> 5) ) & b'\x1f'[0])
    val.insert(0, (block[3] >> 2) & b'\x1f'[0])
    val.insert(0, ( (block[2] << 1) | (block[3] >> 7) ) & b'\x1f'[0])
    val.insert(0, ( (block[1] << 4) | (block[2] >> 4) ) & b'\x1f'[0])
    val.insert(0, (block[1] >> 1) & b'\x1f'[0])
    val.insert(0, ( (block[0] << 2) | (block[1] >> 6) ) & b'\x1f'[0])
    val.insert(0, (block[0] >> 3))

    return val

def b32map_to_string(val_list):
    s = ""

    for i in val_list:
        s = s + b32dict[i]

    return s

def help():
    print("help")
    sys.exit(0)

def main():
    decode = False
    file_n = ""
    block = b''
    in_stream = False
    wrap = 76
    
    if "-h" in sys.argv:
        help()

    if "-d" in sys.argv:
        decode = True

    block = b'\x33\x33\x33\x33\x33'

    file_n = "edit.ini"
    fh_in = open(file_n, mode = 'rb')

    while True:
        block = fh_in.read(5)

        if block == b'':
            break

        byte_n += len(block)

        vals = b23encode_block(block)
        s_str = b32map_to_string(vals)

        if len(block) < 5:
            p = padding[len(block)]
            

    #seq = b32map_to_string(b32encode_block(block))
    #pad_c * padding[len(block)]
   
    #seq = seq[0:]

    print(seq)




    sys.exit(0)


if __name__ == "__main__":
    main()
