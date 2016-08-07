# binenc
Collection of various binary data to text encoders

## `base64`-like encoders
These encoders are designed to be compatible to the feature-set of `base64`, which is a progam available on many UNIXoidal systems. Some expand on the default switch set, but should otherwise be compatible.

To decode, these tools support the `-d` switch.

### `base8.py`
Convert binary data to an alphabet of eight characters.

Every three bits get encoded into a character.

This technically prints a binary file as octal numbers.

### `base16.py`
Convery binary data to an alphabet of sixteen characters.

Every four bits (a "nibble") get encoded into a character.

This technially prints a binary file as hexadecimal numbers.
For all intents and purposes, this kinda works a bit like [`xxd`][1] or [`hexdump`][2],
except it's just the characters, without addresses and/or textual representations, etc.

### `base32.py`
Convert binary data to an alphabet of thirty two characters.

Every five bits get encoded into a character.

A GNU version of this exists already.
I'm doing this primarily as an exercise, to optimize for various encoding bandwidths.

### `base85.py`
Convert binary data to an alphabet of eighty five characters.

Every four bytes get encoded into five characters.
Data is not bit-aligned and is hence taken as 32 bit numbers (big endian) and encoded into a five characters long string, by repeatedly dividing by 85 and taking their reminders, respectively.

This version supports three different alphabets.

## `uuencode`-like encoders
These encoders are designed to be compatible to the feature-set of [`uuencode`][3], which is also available on most UNIXoidal systems.

As with `uuencode` and `uudecode` there exist two version of each, one for encoding and one for decoding.

### `xxencode.py` / `xxdecode.py`
Encode files into [XX encoding][4], which is similar, but not equal to UUencode.

 [1]: http://linuxcommand.org/man_pages/xxd1.html
 [2]: https://enwp.org/Hex_dump
 [3]: https://enwp.org/Uuencoding
 [4]: https://enwp.org/Xxencoding
