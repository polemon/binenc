#! /usr/bin/env python3

import sys
import getopt
import pprint

# encoding alphabets
base85 = { 
    'ascii85' : { 'prefix' : "<~", 'suffix' : "~>", 'zeroblock' : 'z', # Adobe version of 'btoa'
                  'alphabet' : '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstu' },
    'base85'  : { 'prefix' : "", 'suffix' : "", 'zeroblock' : False, # RFC 1924 (1996-04-01)
                  'alphabet' : '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqestuvwxyz!#$%&()*+-;<=>?@^_`{|}~' },
    'z85'     : { 'prefix' : "", 'suffix' : "", 'zeroblock' : False, # ZeroMQ
                  'alphabet' : '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#' }
}

# globals
ver = "base85.py v0.01 (c) Szymon 'polemon' Bereziak"
hlp = """base85.py -- encode / decode data and print to standard output

    Usage:  base85 [SWITCHES] [FILE]

    FILE:
        If FILE is '-', '- -', or omitted, base85.py reads from STDIN
        
        If FILE is '<filename>', or '<filename> -', base85.py will read
        the contents of FILE and print the result to STDOUT

        If FILE are two file names, output will be printed to the
        second file, rather than STDOUT
        
        If FILE is '- <filename>', base85.py will read from STDIN and
        write to the file specified.


    SWITCHES:
      (general)
        -h, --help          This help
        -d, --decode        decode instead of encode
        -v, --version       print short version information
        -w, --wrap=COL      wrap at COL number of characters (def. 76)
                            Use 0 to disable line wrapping. (has no effect
                            when used together with '-d')
        -s, --string=STR    use STR instead of reading from STDIN
        -r, --raw           in case an alphabet uses prefixes and/or
                            postfixes: don't use them

      (alphabet selection)
            --ascii85       use Adobe ascii85 alphabet
            --z85           use ZeroMQ alphabet
            --base85        use RFC 1924 (used for IPv6) alphabet (default)

    Author:      Szymon 'polemon' Bereziak <polemon@gmail.com>
    License:     ISC
    Last change: 2016-08-09
"""

# block is always 4 bytes long
def b85enc_block(encoding, block):
    val = 0

    val = val | (block[0] << (3 * 8))
    val = val | (block[1] << (2 * 8))
    val = val | (block[2] << 8)
    val = val | (block[3])

    e_block = base85[encoding]['alphabet'][val % 85]
    val = int(val / 85)
    e_block = base85[encoding]['alphabet'][val % 85] + e_block
    val = int(val / 85)
    e_block = base85[encoding]['alphabet'][val % 85] + e_block
    val = int(val / 85)
    e_block = base85[encoding]['alphabet'][val % 85] + e_block
    val = int(val / 85)
    e_block = base85[encoding]['alphabet'][val % 85] + e_block

    return e_block

# encoded block is always five characters long
def b85dec_block(encoding, e_block):
    val = 0

    val = val + base85[encoding]['alphabet'].index(e_block[0]) * (85**4)
    val = val + base85[encoding]['alphabet'].index(e_block[1]) * (85**3)
    val = val + base85[encoding]['alphabet'].index(e_block[2]) * (85**2)
    val = val + base85[encoding]['alphabet'].index(e_block[3]) * (85)
    val = val + base85[encoding]['alphabet'].index(e_block[4])

    return bytes([(val >> (8 * 3)), (val >> (8 * 2)) & 255, (val >> 8) & 255, val & 255])

# handle blocks smaller than 4 if necessary
def b85enc_pad(encoding, block):
    if len(block) == 4:
        return b85enc_block(encoding, block)
    else:
        pad = 4 - len(block)
        block = block + bytes([ 0x00 for i in range(pad) ])
        e_block = b85enc_block(encoding, block)
        e_block = e_block[:-pad]
        return e_block

# handle encoded blocks smaller than 5 if necessary
def b85dec_pad(encoding, e_block):
    if len(e_block) == 5:
        return b85dec_block(encoding, e_block)
    else:
        pad = 5 - len(e_block)
        e_block = e_block + ''.join([ base85[encoding]['alphabet'][-1] for i in range(pad) ])
        block = b85dec_block(encoding, e_block)
        block = block[:-pad]
        return block

# get binary block of 4 bytes from stream source
def b85enc_getbinblk(fh):
    barr = bytearray()

    byte = fh.read(1)
    while byte != b'' and len(barr) < 3:
        barr += byte
        byte = fh.read(1)

    barr += byte
    return bytes(barr)

# wraps lines correctly, and recalculated new line length if necessary
def b85enc_print(fh_out, linlen, wrap, s):
    while linlen > wrap and wrap != 0:    # very smart version of an if-then-else ;)
        part = wrap - (linlen -len(s))

        fh_out.write(s[:part].encode())
        fh_out.write(b'\n')
        fh_out.flush()

        s = s[part:]
        linlen = len(s)

        # word wrapping like this also works with blocks larger than a single line:
        # line length = 4 and block size = 5
        # wrap == 0 is no wrapping
 
    fh_out.write(s.encode())
    fh_out.flush()

    return linlen

# encode stream, print to output stream
# also, honor word wrapping
# note default values
def b85enc(fh_in = sys.stdin.buffer, fh_out = sys.stdout.buffer, encoding = 'ascii85', wrap = 76, raw = False):
    linlen = 0

    if not raw:
        linlen = b85enc_print(fh_out, len(base85[encoding]['prefix']), wrap, base85[encoding]['prefix'])

    blk = b85enc_getbinblk(fh_in)
    s = b85enc_pad(encoding, blk)
    linlen += len(s)

    while len(blk) != 0:    # empty block received at EOF
        linlen = b85enc_print(fh_out, linlen, wrap, s)

        blk = b85enc_getbinblk(fh_in)
        s = b85enc_pad(encoding, blk)
        linlen += len(s)

    if not raw:
        linlen += len(base85[encoding]['suffix']) -1    # the one overhang is an empy bye from EOF
        b85enc_print(fh_out, linlen, wrap, base85[encoding]['suffix'])

# handle string from cli as input and print result to output stream
def b85enc_str(binstr = b'', fh_out = sys.stdout.buffer, encoding = 'ascii85', wrap = 76, raw = False):
    idx = 0
    linlen = 0

    if not raw:
        linlen = b85enc_print(fh_out, len(base85[encoding]['prefix']), wrap, base85[encoding]['prefix'])

    while idx < len(binstr):
        blk = binstr[idx:idx+4]
        s = b85enc_pad(encoding, blk)
        linlen += len(s)

        linlen = b85enc_print(fh_out, linlen, wrap, s)

        idx += 4
    
    if not raw:
        linlen += len(base85[encoding]['suffix'])    # the one overhang is an empy bye from EOF
        b85enc_print(fh_out, linlen, wrap, base85[encoding]['suffix'])

# get chunk (5 characters) of encoded data from input source and disregard whitespace characters
def b85dec_getblk(fh):
    s = ""
    
    byte = fh.read(1)
    while True: # emulating a do-while loop
        c = byte.decode()

        if not c.isspace(): # disregard white space characters (these must be silently ignored)
            s += c
        if byte == b'' or len(s) >= 5:  # while part of the do-while loop
            break

        byte = fh.read(1)

    return s

# FIXME no prefix encoding understood!
def b85dec(fh_in = sys.stdin.buffer, fh_out = sys.stdout.buffer, encoding = 'ascii85', raw = False):
    e_block = b85dec_getblk(fh_in)

    while e_block:
        b = b85dec_pad(encoding, e_block)
        fh_out.write(b)
        fh_out.flush()
        e_block = b85dec_getblk(fh_in)

# FIXME no prefix encoding understood!
def b85dec_str(e_binstr = '', fh_out = sys.stdout.buffer, encoding = 'ascii85', raw = False):
    idx = 0
    
    if not raw:
        pass

    while idx < len(e_binstr):
        e_block = ""
        
        while len(e_block) < 5 and idx < len(e_binstr):
            c = e_binstr[idx]
            if not c.isspace():
                e_block += c
            
            idx += 1

        b = b85dec_pad(encoding, e_block)
        fh_out.write(b)
        fh_out.flush()

    # print(e_binstr)

def main():
    sys.argv.pop(0) # get rid of script name

    # standard values not actually necessary in library use
    fh_in = sys.stdin.buffer
    fh_out = sys.stdout.buffer
    encoding = 'ascii85'
    wrap = 76

    # defaults
    binstr = b''
    decode = False
    raw = False

    try:
        sw, arg = getopt.getopt(sys.argv, 'hdrvw:s:', ['help', 'decode', 'raw', 'version', 'wrap=', 'string=', 'ascii85', 'z85', 'base85'])
    except getopt.GetoptError as e:
        print("ERROR:", e)
        exit(1)

    # parse switch settings
    for s, o in sw:
        if s in  ('-w', '--wrap'):
            wrap = int(o)
            if wrap < 0:
                print("ERROR: word wrapping column number must be positive or 0!", file = sys.stderr)
                exit(1)
        elif s in ('-s', '--string'):   # treat things in that paramter as bytes at all times
            binstr = o.encode(sys.getfilesystemencoding(), 'surrogateescape')
        elif s in ('--ascii85'):
            encoding = 'ascii85'
        elif s in ('--base85'):
            encoding = 'base85'
        elif s in ('--z85'):
            encoding = 'z85'
        elif s in ('-d', '--decode'):
            decode = True
        elif s in ('-r', '--raw'):
            raw = True
        elif s in ('-v', '--version'):
            print(ver)
            exit(0)
        elif s in ('-h', '--help'):
            print(hlp)
            exit(0)
        else:
            print("ERROR: something FUBAR with the switches, I'll show you later...", file = sys.stderr)
            exit(1)

    if decode:
        if binstr:
            b85dec_str(e_binstr = binstr.decode(), fh_out = fh_out, encoding = encoding, raw = raw)
        else:
            b85dec(fh_in = fh_in, fh_out = fh_out, encoding = encoding, raw = raw)
    else:
        if binstr:
            b85enc_str(binstr = binstr, fh_out = fh_out, encoding = encoding, wrap = wrap, raw = raw)
        else:
            b85enc(fh_in = fh_in, fh_out = fh_out, encoding = encoding, wrap = wrap, raw = raw)

    #pprint.pprint(sw)

    #byte = sys.stdin.buffer.read(1)
    #while byte != b'':
    #    pprint.pprint(byte)
    #    byte = sys.stdin.buffer.read(1)


#    pprint.pprint(sys.argv)
#    pprint.pprint(len(sys.argv[0]))
#    pprint.pprint(0 if len(sys.argv[0]) % 4 == 0 else 4 - len(sys.argv[0]) % 4)

#    pprint.pprint(sys.argv[0].encode()
#    encoded = b85enc_pad('base85', sys.argv[0].encode())

if __name__ == '__main__':
    main()
