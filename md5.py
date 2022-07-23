# MD5

__all__ = ['MD5']

from msmath.bitstring import bitstrings
bitstring = bitstrings(32)

from msmath.rational import sin

from msmath.conversions import xrange

T = tuple(bitstring(int(abs(sin(i+1))<<32),32) for i in xrange(64));

F = (lambda x,y,z : x&y|~x&z,
     lambda x,y,z : x&z|y&~z,
     lambda x,y,z : x^y^z,
     lambda x,y,z : y^(x|~z)
    );

S = ((7,12,17,22),
     (5,9,14,20),
     (4,11,16,23),
     (6,10,15,21)
    );

X = (lambda k : k,
     lambda k : (5*k+1)&15,
     lambda k : (3*k+5)&15,
     lambda k : (7*k)&15
    );

blocksize = 512;
wordsize = 32;
lensize = 64;
wpb = blocksize//wordsize;

H0 = bitstring(0x67452301efcdab8998badcfe10325476,128);

def MD5(M) :
  """Return, as a bitstring, MD5 hash of a string or bitstring, as per RFC1321"""
  M = bitstring(M);    # make a copy, or convert a string
  l = len(M);    # if this isn't a multiple of 8, endianness may be an issue!
  M = M.iconcat(1);    # pad to multiple of blocksize ...
  M.itrunc((l+blocksize+lensize)//blocksize*blocksize-lensize);
  L = bitstring(l,64).split(8);    # big-endian length field
  M.iconcat(*L[::-1]);       # -> little-endian
  M = M.split(blocksize);
  N = len(M)//wpb;
  H = H0.split(wordsize);
  for i,B in enumerate(M) :    # for each message block
    B = B.split(wordsize);
    for i,b in enumerate(B) :    # rearrange octets in words
      o = b.split(8);
      B[i] = bitstring.concat(*o[::-1]);
    I = tuple(map(bitstring,H));    # save a copy of digest so far
    for j in xrange(4) :    # for each pass
      for k in xrange(wpb) :    # for each word in message block
        H[-k&3] = H[(1-k)&3]+((H[-k&3]+F[j](H[(1-k)&3],H[(2-k)&3],H[(3-k)&3])+
                               B[X[j](k)]+T[16*j+k])<<S[j][k&3]);
    for i,h in enumerate(I) :    # update digest
      H[i] += h;
  for i,h in enumerate(H) :    # convert back to big-endian
    o = h.split(8);
    H[i] = bitstring.concat(*o[::-1]);
  return bitstring.concat(*H);

if __name__=='__main__' :
  MD5d = {  # Test suite from RFC1321:
    '' : 0xd41d8cd98f00b204e9800998ecf8427e,
    'a' : 0x0cc175b9c0f1b6a831c399e269772661,
    'abc' : 0x900150983cd24fb0d6963f7d28e17f72,
    'message digest' : 0xf96b697d7cb7938d525a2f31aaf161d0,
    'abcdefghijklmnopqrstuvwxyz' : 0xc3fcd3d76192e4007dfb496cca67e13b,
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789' : 0xd174ab98d277d9f5a5611c2c9f419d9f,
    '1234567890'*8 : 0x57edf4a22be3c955ac49da2e2107b67a,
  };
  success = True;
  for k,v in MD5d.items() :
    if MD5(k) != bitstring(v,128) :
      print('MD5(%s) failed'%(k));
      success = False;
  if success :
    print('MD5 passed');
    
