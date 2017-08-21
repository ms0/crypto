# crypto
Crypto-related python routines, for exposition, not performance

Dependency: rational.py from pymath repository (for computing constants in SHA2.py)

SHA2.py contains code for algorithms described in NIST.FIPS.180-4

SHA3.py contains code for algorithms described in NIST.FIPS.202

shatest.py runs SHA2 and SHA3 with various test vectors and prints the results

bitstring.py implements the bitstring class whose instances are each a sequence of bits,
indexed starting at 0.
The constructor can create a bitstring instance from a bitstring (a copy),
a string (converting each character c to ord(c) and assuming it to be 8 bits long),
or an integer (with big-endian bit numbering) together with a number of bits.
Examples:
bitstring('abc') -> 011000010110001001100011 [printed as 616263]
bitstring(0x37,7) -> 0110111 [printed as 37]

bitstring instances have the following attributes:
 .x the bitstring interpreted as a big-endian integer
 ._l the number of bits in the bitstring (same as len())
 Specifically for use by SHA3, if ._l is 25*2**l for some integer l, then
  .b same as ._l
  .w ._l/25
  .l log(._l/25)
  
In the bitstring class, the following operators are defined:
 len() the length of the bitstring, in bits
 - negation mod 2**length
 ~ bitwise complement
 + addition mod 2**length
 - subtraction mod 2**length
 ^ bitwise exclusive or
 & bitwise and
 | bitwise or
 <<k  rotate left k bit positions [not shift!]
 >>k  rotate right k bit positions [not shift!]
 *k concatenate k copies
 int() the bitstring as a big-endian number
 [sequence of indices and slices]  the bitstring of the concatenated selected bits
 [sequence of indices and slices] = bitstring or integer  the selected bits are set
In the bitstring class, the following functions are defined:
 .concat(sequence of bitstrings and 0s and 1s)
   returns the bitstring resulting from concatenating the bitstring with the sequence of bits and bitstrings
 .tacnoc(sequence of bitstrings and 0s and 1s)
   returns the bitstring resulting from concatenating the reversed sequence of bits and bitstrings with the bitstring
 .trunc(n) equivalent to [:n], but checks that n <= ._l

bitstring.py also implements the following functions:
 c2bs() converts a character to an 8-bit bitstring
 s2bs() converts a string to a bitstring, using c2bs
 b3x takes a bitstring and produces a new bitstring by reversing each sequence of 8 bits,
   with any remaining bits also reversed;
   this can be used to compensate for the little-endian specification of SHA3 (see shatest.py)

bitstring.py also implements the plane class, specifically for SHA3
