# __all__ = ['rijndael','AES','AES128','AES192','AES256']

"""Note to self: we have to figure out which coefficients are which,
  particularly for keys and mixcolumn
  Answer: for mixcolumn, top is constant, bottom is hi order
  So octets are in little-endian order.
  Within an octet (as normally written) the msb is first.
  We have to be careful as we manipulate 4-octet quantities as a 32-bit string.
"""


from conversions import unpack,pack,xrange
from numfuns import m2mul
from ffield import ffield
from poly import polynomial
from bitstring import bitstrings

bitstring = bitstrings(32);

def _x(x) :    # different from ffield._x, so can handle integer x = 0
  """Return _x attribute of x if x, else 0"""
  return x._x if x else 0;

def packpoly(p) :
  """Given a polynomial, pack it so constant coeff is least significant nibble"""
  if not p : return 0;
  return pack(p[0].q,map(_x,reversed(p)));

def unpackpoly(F,p) :
  """Given F, and packed polynomial over F, unpack into polynomial"""
  return polynomial(*unpack(F.q,p)).mapcoeffs(F);

def poly2w(p) :
  """Given a degree-4 polynomial, pack it so constant coeff is most significant"""
  if not p : return 0;
  return pack(p[0].q,map(_x,p[:4]));

def w2poly(F,p) :
  """Given a packed word of F coefficients, unpack into polynomial"""  
  return polynomial(*unpack(F.q,p+(1<<32))[4:0:-1]).mapcoeffs(F);

B = 0xff;

GF2 = ffield(2);
GF8 = ffield(2,8,0x1b);

x = GF8(2);
C = [(x**i).x for i in xrange(30)];    # for key expansion

m = GF8.polynomial;
c = polynomial(3,1,1,2).mapcoeffs(GF8);    # MixColumn
x4p1 = polynomial(1,0,0,0,1).mapcoeffs(GF8);
d = x4p1.xgcd(c)[-1];


# Compute sbox and inverse sbox #
x = polynomial(1,0).mapcoeffs(GF2);
m1 = x**8+1;
p1 = (x**5-1)/(x-1);
a = x**6+x**5+x+1;
# p2 = m1.xgcd(p1)[-1];
sbox = [0]*256;
rbox = [0]*256;
for i in xrange(256) :
  j = GF8(i)
  j = packpoly((j and j**-1).polynomial*p1%m1+a);
  sbox[i] = j;
  rbox[j] = i;

def MixColumn(x) :
  """Apply MixColumn to 32-bit value x"""
  return poly2w(w2poly(GF8,int(x))*c%x4p1);

def InvMixColumn(x) :
  """Apply InvMixColumn to 32-bit value x"""
  return poly2w(w2poly(GF8,int(x))*d%x4p1);

def MixColumns(x) :
  for i in xrange(0,len(x),32) :
    x[i:i+32] = MixColumn(x[i:i+32]);

def InvMixColumns(x) :
  for i in xrange(0,len(x),32):
    x[i:i+32] = InvMixColumn(x[i:i+32]);

def ColSub(w) :
  return (sbox[w>>24]<<24)|(sbox[(w>>16)&B]<<16)|(sbox[(w>>8)&B]<<8)|sbox[w&B];

def ColRub(w) :
  return (rbox[w>>24]<<24)|(rbox[(w>>16)&B]<<16)|(rbox[(w>>8)&B]<<8)|rbox[w&B];

def ByteSub(x) :
  for i in range(0,len(x),32) :
    x[i:i+32] = bitstring(ColSub(int(x[i:i+32])),32);

def InvByteSub(x) :
  for i in range(0,len(x),32) :
    x[i:i+32] = bitstring(ColRub(int(x[i:i+32])),32);

def keyexpand(key,n) :    # expand key to n 32-bit round keys
  Nk = len(key)//32;
  keys = [0]*n;
  for i in xrange(Nk) :
    keys[i] = int(key[i<<5:(i+1)<<5]);
  try :
    for i in xrange(0,n,Nk) :
      k = keys[i+Nk-1];
      k = (sbox[k>>24] | (sbox[k&B]<<8) | (sbox[(k>>8)&B] << 16) |
           ((sbox[(k>>16)&B]^C[i//Nk]) << 24));
      for j in xrange(Nk) :
        if Nk > 6 and j==4 :
          k = ColSub(k);
        k ^= keys[i+j];
        keys[i+j+Nk] = k;
  except IndexError :
    pass;
  return keys;    

class rijndael(object) :

  def __init__(self,key,Nb=None,Nr=None) :
    self.Nk,r = divmod(len(key),32);
    if r or not key :
      raise ValueError('keylength must be positive multiple of 32')
    self.Nb = Nb or 4;
    self.Nr = Nr or 6+max(self.Nb,self.Nk);
    keys = keyexpand(key,(self.Nr+1)*self.Nb);    # expand key
    self.keys = [bitstring() for _ in xrange(self.Nr+1)];
    for i,b in enumerate(self.keys) :
      for j in xrange(self.Nb) :
        b.iconcat(bitstring(keys[i*self.Nb+j],32));

  def rowslices(self,i) :
    return tuple(slice(8*i+j*32,8*i+8+j*32) for j in range(self.Nb));

  def ShiftRows(self,x) :
    x[self.rowslices(1)] = x[self.rowslices(1)] << 8;
    x[self.rowslices(2)] = x[self.rowslices(2)] << (2+self.Nb//8)*8;
    x[self.rowslices(3)] = x[self.rowslices(3)] << (3+self.Nb//7)*8;

  def InvShiftRows(self,x) :
    x[self.rowslices(1)] = x[self.rowslices(1)] >> 8;
    x[self.rowslices(2)] = x[self.rowslices(2)] >> (2+self.Nb//8)*8;
    x[self.rowslices(3)] = x[self.rowslices(3)] >> (3+self.Nb//7)*8;

  def encrypt(self,x) :
    x = bitstring(x);
    x ^= self.keys[0];
    for r in xrange(1,self.Nr) :
      ByteSub(x);
      self.ShiftRows(x);
      MixColumns(x);
      x ^= self.keys[r];
    ByteSub(x);
    self.ShiftRows(x);
    x ^= self.keys[self.Nr];
    return x;

  def decrypt(self,x) :
    x = bitstring(x);
    x ^= self.keys[self.Nr];
    for r in xrange(self.Nr-1,0,-1) :
      InvByteSub(x);
      self.InvShiftRows(x);
      x ^= self.keys[r];
      InvMixColumns(x);
    InvByteSub(x);
    self.InvShiftRows(x);
    x ^= self.keys[0];
    return x;

def AES(key) :
  return rijndael(key);

def AES128(key) :
  return AES(bitstring(key,128));

def AES192(key) :
  return AES(bitstring(key,192));

def AES256(key) :
  return AES(bitstring(key,256));

def tryAES(key,plaintext) :
  for key in (key,key.concat(key[:64]),key.concat(key)) :
    a = AES(key);
    c = a.encrypt(bitstring(int(plaintext),128));
    d = a.decrypt(c);
    print('key:',hex(int(key)))
    print('plaintext',hex(int(plaintext)))
    print('ciphertext',hex(int(c)))
    print('decrypted',hex(int(d)))

"""Test vectors (128 bits)
NOTE: these seem to use some sort of mode other than ECB;
current code agrees with aes.py raw encrypt for 128, 192,and 256"""

KEY = bitstring(0x8d2e60365f17c7df1040d7501b4a7b5a,128)
PLAINTEXT = bitstring(0x59b5088e6dadc3ad5f27a460872d5929,128)
"""
CIPHERTEXT = a02600ecb8ea77625bba6641ed5f5920
KEY = 2d0860dae7fdb0bd4bfab111f615227a
PLAINTEXT = a02600ecb8ea77625bba6641ed5f5920
CIPHERTEXT = 5241ead9a89ca31a7147f53a5bf6d96a
KEY = 7f498a034f6113a73abd442bade3fb10
PLAINTEXT = 5241ead9a89ca31a7147f53a5bf6d96a
CIPHERTEXT = 22f09171bc67d0661d1c25f181a69f33
"""

