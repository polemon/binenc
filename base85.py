#! /usr/bin/env python3

import sys
import getopt
import pprint

base85 = { 
    'ascii85' : { 'prefix' : "<~", 'suffix' : "~>", 'zeroblock' : 'z', # Adobe version of 'btoa'
                  'alphabet' : '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstu' },
    'base85'  : { 'prefix' : "", 'suffix' : "", 'zeroblock' : False, # RFC 1924 (1996-04-01)
                  'alphabet' : '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqestuvwxyz!#$%&()*+-;<=>?@^_`{|}~' },
    'z85'     : { 'prefix' : "", 'suffix' : "", 'zeroblock' : False, # ZeroMQ
                  'alphabet' : '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#' }
}

# default values
wrap = 76
alph = 'ascii85'

hlp = """base85 -- encode / decode data and print to standard output

    Usage:  base85 [SWITCHES] [FILE]

    FILE:
        If FILE is '-' or omitted, base85 reads from STDIN
        otherwise it'll encode the contents of FILE and print to
        STDOUT

    SWITCHES:
      (general)
        -h, --help          This help
        -d, --decode        decode instead of encode
        -v, --version       print short version information
        -w, --wrap=COL      wrap at COL number of characters (def. 76).
                            Use 0 to disable line wrapping.
        -s, --string=STR    use STR instead of reading from STDIN

      (alphabet selection)
            --ascii85       use Adobe ascii85 alphabet
            --z85           use ZeroMQ alphabet
            --base85        use RFC 1924 (used for IPv6 adresses) alphabet (default)

    Author:      Szymon 'polemon' Bereziak <polemon@gmail.com>
    License:     ISC
    Last change: 2016-07-31
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

    val = val + base85[encoding]['alphabet'].index(e_block[0]) * 85**4
    val = val + base85[encoding]['alphabet'].index(e_block[1]) * 85**3
    val = val + base85[encoding]['alphabet'].index(e_block[2]) * 85**2
    val = val + base85[encoding]['alphabet'].index(e_block[3]) * 85
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

# encode stream, print to output stream
def b85enc(fh_in, fh_out, encoding):
    blk = b85enc_getbinblk(fh_in)
    s = b85enc_pad(encoding, blk)
    linlen = len(s)

    while len(blk) != 0:
        fh_out.write(b'|')
        if linlen > wrap:
            #if wrap % (linlen -5):
                #pprint.pprint(linlen)
                #pprint.pprint(wrap)
            part = wrap % (linlen -5)
                #fh_out.write(("-part%d-" % part).encode())
                #pprint.pprint(linlen -5)
                #print()
                #pprint.pprint(s[:part] + '\n' + s[part:])
            fh_out.write(s[:part].encode())
            fh_out.write(b'\n')

            s = s[part:]
                #fh_out.write('``'.encode())
            linlen = len(s)
            #else:
                #fh_out.write(b'\n')
            
            #    linlen = len(s)
                #pass

        
        fh_out.write(s.encode())
        fh_out.flush()
        blk = b85enc_getbinblk(fh_in)
        s = b85enc_pad(encoding, blk)
        linlen += len(s)
        

def main():
    sys.argv.pop(0) # get rid of script name

    #pprint.pprint(sys.argv[0])
    global wrap

    try:
        sw, arg = getopt.getopt(sys.argv, 'hdvw:s:', ['help', 'decode', 'version', 'wrap=', 'string=', 'ascii85', 'z85', 'base85'])
    except getopt.GetoptError as e:
        print("ERROR:", e)
        exit(1)

    for s, o in sw:
        if s in  ('-w', '--wrap'):
            wrap = int(o)


    pprint.pprint(sw)

    #byte = sys.stdin.buffer.read(1)
    #while byte != b'':
    #    pprint.pprint(byte)
    #    byte = sys.stdin.buffer.read(1)

    b85enc(sys.stdin.buffer, sys.stdout.buffer, 'ascii85')

#    pprint.pprint(sys.argv)
#    pprint.pprint(len(sys.argv[0]))
#    pprint.pprint(0 if len(sys.argv[0]) % 4 == 0 else 4 - len(sys.argv[0]) % 4)

#    pprint.pprint(sys.argv[0].encode()
#    encoded = b85enc_pad('base85', sys.argv[0].encode())

#    pprint.pprint(encoded)

#    print("re-decoded:")
#    pprint.pprint(b85dec_pad('base85', encoded))

    #print(hlp)
    #pprint.pprint(sw)
    #pprint.pprint(arg)

    pass

if __name__ == '__main__':
    main()
