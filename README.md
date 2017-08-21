# crypto
Crypto-related python routines, for exposition, not performance

Dependency: rational.py from pymath repository (for computing constants in SHA2.py)

SHA2.py contains code for algorithms described in NIST.FIPS.180-4

SHA3.py contains code for algorithms described in NIST.FIPS.202

shatest.py runs SHA2 and SHA3 with various test vectors and prints the results

bitstring.py implements the bitstring class whose instances are each a sequence of bits,<br>
indexed starting at 0.<br>
The constructor can create a bitstring instance from a bitstring (a copy),<br>
a string (converting each character c to ord(c) and assuming it to be 8 bits long),<br>
or an integer (with big-endian bit numbering) together with a number of bits.<br>
Examples:<br>
bitstring('abc') -> 011000010110001001100011 [printed as 616263]<br>
bitstring(0x37,7) -> 0110111 [printed as 37]<br>

bitstring instances have the following attributes:<br>
 .x the bitstring interpreted as a big-endian integer<br>
 ._l the number of bits in the bitstring (same as len())<br>
 Specifically for use by SHA3, if ._l is 25*2**l for some integer l, then<br>
  .b same as ._l<br>
  .w ._l/25<br>
  .l log(._l/25)<br>
  
In the bitstring class, the following operators are defined:<br>
 len() the length of the bitstring, in bits<br>
 - negation mod 2**length<br>
 ~ bitwise complement<br>
 + addition mod 2**length<br>
 - subtraction mod 2**length<br>
 ^ bitwise exclusive or<br>
 & bitwise and<br>
 | bitwise or<br>
 <<k  rotate left k bit positions [not shift!]<br>
 >>k  rotate right k bit positions [not shift!]<br>
 *k concatenate k copies<br>
 int() the bitstring as a big-endian number<br>
 [sequence of indices and slices]  the bitstring of the concatenated selected bits<br>
 [sequence of indices and slices] = bitstring or integer  the selected bits are set<br>
In the bitstring class, the following functions are defined:<br>
 .concat(sequence of bitstrings and 0s and 1s)<br>
   returns the bitstring resulting from concatenating the bitstring with the sequence of bits and bitstrings<br>
 .tacnoc(sequence of bitstrings and 0s and 1s)<br>
   returns the bitstring resulting from concatenating the reversed sequence of bits and bitstrings with the bitstring<br>
 .trunc(n) equivalent to [:n], but checks that n <= ._l<br>

bitstring.py also implements the following functions:<br>
 c2bs() converts a character to an 8-bit bitstring<br>
 s2bs() converts a string to a bitstring, using c2bs<br>
 b3x takes a bitstring and produces a new bitstring by reversing each sequence of 8 bits,<br>
   with any remaining bits also reversed;<br>
   this can be used to compensate for the little-endian specification of SHA3 (see shatest.py)<br>

bitstring.py also implements the plane class, specifically for SHA3
