# crypto
Crypto-related python routines, for exposition, not performance

Dependencies: rational.py and ffield.py from pymath repository (for computing constants in SHA2.py, for various uses in rsa.py)

rc4.py contains code for the RC4 one-time pad generator

rsa.py contains code for creating and using RSA key pairs

sha2.py contains code for algorithms described in NIST.FIPS.180-4, including SHA1 and SHA2 family

sha3.py contains code for algorithms described in NIST.FIPS.202, including SHAKE and SHA3 family

shatest.py runs SHA1, SHA2, and SHA3 with various test vectors and prints the results

bitstring.py implements the bitstring class whose instances are each a sequence of bits,<br>
indexed starting at 0.

Use python help for more current and complete documentation.

The bitstring constructor can create a bitstring instance from a bitstring (a copy),<br>
a string (converting each character c to ord(c) and assuming it to be 8 bits long),<br>
or an integer (with big-endian bit numbering) together with a number of bits.

Examples:<br>
bitstring('abc') -> 011000010110001001100011 [printed as 0x616263]<br>
bitstring(0x37,7) -> 0110111 [printed as 0x37]<br>

bitstring instances have the following attributes:
<table>
 <tr><td>.x</td><td>the bitstring interpreted as a big-endian integer</td></tr>
 <tr><td>._l</td><td>the number of bits in the bitstring (same as len())</td></tr>
 </table>
  
In the bitstring class, the following operators are defined:<br>
<table>
<tr><td> len()</td><td> the length of the bitstring, in bits</td></tr>
<tr><td> -</td><td> negation mod 2**length</td></tr>
<tr><td> ~</td><td> bitwise complement</td></tr>
<tr><td> +</td><td> addition mod 2**length</td></tr>
<tr><td> -</td><td> subtraction mod 2**length</td></tr>
<tr><td> ^</td><td> bitwise exclusive or</td></tr>
<tr><td> &</td><td> bitwise and</td></tr>
<tr><td> |</td><td> bitwise or</td></tr>
<tr><td> &lt;&lt;k</td><td>  rotate left k bit positions [not shift!]</td></tr>
<tr><td> &gt;&gt;k</td><td>  rotate right k bit positions [not shift!]</td></tr>
<tr><td> *k</td><td> concatenate k copies</td></tr>
<tr><td> int()</td><td> the bitstring as a big-endian number</td></tr>
<tr><td> [sequence of indices and slices]</td><td>  the bitstring of the concatenated selected bits</td></tr>
<tr><td> [sequence of indices and slices] = bitstring or integer </td><td> the selected bits are set</td></tr>
</table>

In the bitstring class, the following functions are defined:
<table>
<tr><td> .concat(sequence of bitstrings and 0s and 1s)</td>
   <td>returns the bitstring resulting from concatenating the bitstring with the sequence of bits and bitstrings</td></tr>
<tr><td> .tacnoc(sequence of bitstrings and 0s and 1s)</td>
   <td>returns the bitstring resulting from concatenating the reversed sequence of bits and bitstrings with the bitstring</td></tr>
<tr><td> .trunc(n) </td><td>equivalent to [:n] if 0 <= n <= ._l, else if n >= 0, concatenate 0s so resulting length is always exactly n</td></tr>
<tr><td></td><td>if n < 0, truncate from the left or concatenate 0s on the left so that the resulting length is always exactly -n</td></tr>
</table>

sha3.py also implements the following function:
<table>
<tr><td> b3x()</td><td> takes a bitstring and produces a new bitstring by reversing each sequence of 8 bits, with any remaining bits also reversed;
   this can be used to compensate for the little-endian specification of SHA3 (see shatest.py)</td></tr>
</table>

sha3.py also implements the plane class
