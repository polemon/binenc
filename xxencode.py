#! /usr/bin/env python3
"""
    xxencode.py - encode file into xxencoding

    Author:      Szymon 'polemon' Bereziak <polemon@gmail.com>
    Version:     0.01
    Last Change: 2016-01-09

"""

import os
import sys
import getopt
from stat import *

xxdict = "+-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

halp = """xxencode -- encode into xxencoding

Usage:
    xxencode [INFILE] [OUTFILE]

Args:
    (no args)
    INFILE = '-'
        read from STDIN, print to STDOUT

    INFILE = somefile.bin
        read somefile.bin, write to somefile.bin.xx

    Setting either INFILE and/or OUTFILE to '-'
        use STDIN and STDOUT, respectively.

    -h
        this help.

(c) 2016 - Szymon 'polemon' Bereziak <polemon@gmail.com>"""

# this transforms a block of <=3 octets into 4 sextets.
def xxencode_block(block):
    val = list()
    
    for i in range(len(block), 3):
        block += b'\x00'

    val.insert(0, block[2] & b'\x3f'[0])
    val.insert(0, ( (block[1] << 2) | (block[2] >> 6) ) & b'\x3f'[0])
    val.insert(0, ( (block[0] << 4) | (block[1] >> 4) ) & b'\x3f'[0])
    val.insert(0, (block[0] >> 2))
    
    return val

# this maps sextets to XXencoding symbols 
def xxmap_to_string(val_list):
    s = ""

    for i in val_list:
        s = s + xxdict[i]

    return s 

def help():
    print(halp)
    sys.exit(0)

def main():
    block = b''
    byte_n = 0
    in_stream = False
    file_n = ""
    out_stream = True
    o_file_n = ""

    # param checking
    if "-h" in sys.argv:
        help()

    if len(sys.argv) <= 1:
        in_stream = True
        out_stream = True
    elif len(sys.argv) == 2:
        if sys.argv[1] == "-":
            in_stream = True
            out_stream = True
        else:
            in_stream = False
            out_stream = False
            file_n = sys.argv[1]
            o_file_n = file_n + ".xx"
    elif len(sys.argv) == 3:
        if sys.argv[1] == "-":
            in_stream = True
        else:
            in_stream = False
            file_n = sys.argv[1]

        if sys.argv[2] == "-":
            out_stream = True
        else:
            out_stream = False
            o_file_n = sys.argv[2]
    else:
        help()

    # this is the first line in a XXencoded file
    begin_l = "begin"

    # check / setup file handlers / streams
    if not in_stream:
        try:
            fh_in = open(file_n, mode = 'rb')
        except IOError:
            print("can't open file " + file_n)
            sys.exit(1)

        begin_l += " " +  str(oct(os.stat(file_n).st_mode & 0o777))[-3:] + " " + file_n
    else:
        fh_in = sys.stdin.buffer
   
    if not out_stream:
        try:
            fh_out = open(o_file_n, mode = 'w')
        except IOError:
            print("can't open file " + o_file_n)
            sys.exit(1)
    else:
        fh_out = sys.stdout

    #print("===================================")
    #print("  in_stream = " + str(in_stream))
    #print(" out_stream = " + str(out_stream))
    #print("     file_n = " + file_n)
    #print("   o_file_n = " + o_file_n)
    #print("===================================")
    #print()

    # write first line of XXencoded file
    fh_out.write(begin_l + '\n')

    # read data in chunks of 3 bytes and process them
    xxline = ""
    while True:
        block = fh_in.read(3)
    
        if block == b'':
            fh_out.write(xxdict[byte_n] + xxline + '\n')
            break

        #print(len(block))
        byte_n += len(block)
        vals = xxencode_block(block)
        s_str = xxmap_to_string(vals)
        
        # XXencodings are no longer than 45 (original bytes) per line
        if byte_n == 45:
            byte_n = 0
            fh_out.write('h' + xxline + s_str + '\n')
            xxline = ""
        else:
            xxline = xxline + s_str

    # end of file marker
    fh_out.write("end\n")

    # close files
    if not in_stream:
        fh_in.close()

    if not out_stream:
        fh_out.close()

if __name__ == '__main__':
    main()
