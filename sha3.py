# SHA-3 implementation

import sys

if sys.version_info[0] >= 3 :
  xrange = range;

from bitstring import bitstrings
bitstring=bitstrings(1600);

from math import log
rlog2 = lambda x: int(round(log(x,2)));
is2power = lambda x: x&-x == x;

################################################################
# sha3 array
# a.x is bitstring for array
# a[x,y,z] is a bit that can be read and set
# a.plane(i)

class sharray(object) :
  """SHA3 array class"""

  def __init__(self,arg) :
    """Create a sha3 state array from a sharray or bitstring; sharray is copied"""
    if isinstance(arg,sharray) :
      self.x = type(arg.x)(arg.x);    # copy bitstring
    elif type(type(arg)) == bitstrings :
      # assume not arg._l%25 and is2power(arg._l//25)
      self.x = arg;    # don't copy bitstring
    else :
      raise TypeError('arg must be sharray or bitstring of compatible size');

  def __str__(self) :
    """Return a string representing sharray self"""
    return str(self.x);

  def __repr__(self) :
    """Return a string representing sharray self"""
    return 'sharray('+repr(self.x)+')';

  def __eq__(self,other) :
    """Return True iff self and other are sharrays with same content"""
    return type(self) == type(other) and self.x == other.x;

  def __ne__(self,other) :
    """Return False iff self and other are sharrays with same content"""
    return type(self) != type(other) or self.x != other.x;

  def __len__(self) :
    """Return the number of bits in self"""
    return self.x._l;

  def __getitem__(self,key) :
    """Get the keyth bit of state array self; key is x,y,z
    If z is a slice, return the corresponding bitstring"""
    x,y,z = key;
    l = self.x._l//25;
    w = l*(5*y+x);
    if isinstance(z,slice) :
      s = z.indices(l);
      return self.x[w+s[0]:w+s[1]:s[2]];
    return int(self.x[w+z]);

  def __setitem__(self,key,b) :
    """Set the keyth bit of state array self; key is x,y,z
    If z is a slice, b should be a bitstring"""
    x,y,z = key;
    l = self.x._l//25;
    w = l*(5*y+x)
    if isinstance(z,slice) :
      s = z.indices(l);
      self.x[w+s[0]:w+s[1]:s[2]] = b;
    else :
      self.x[w+z] = b;

  def plane(self,i) :
    """Return a copy of the ith plane of state array self"""
    x = self.x;
    p = x._l//5;
    io = p*i;
    return plane(x[io:io+p]);

################################################################
# sha3 plane
# .x is bitstring for plane
# [x,z] can be read and set

class plane(object) :
  """SHA3 plane class"""

  def __init__(self,arg) :
    """Create a sha3 plane from a plane or a bitstring; bitstring is not copied"""
    if isinstance(arg,plane) :
      self.x = type(arg.x)(arg.x);    # copy bitstring
    elif type(type(arg)) == bitstrings :
      # assume not arg._l%5 and is2power(arg._l//5)
      self.x = arg;    # don't copy bitstring
    else :
      raise TypeError('arg must be plane or bitstring of compatible size');

  def __str__(self) :
    """Return a string representing plane self"""
    return str(self.x);

  def __repr__(self) :
    """Return a string representing plane self"""
    return 'plane('+repr(self.x)+')';

  def __getitem__(self,key) :
    """Return the keyth bit of plane self, addressed as x,z
    If z is a slice, return the corresponding bitstring"""
    x,z = key;
    s = self.x;
    m = s._l//5;
    w = m*x;
    if isinstance(z,slice) :
      t = z.indices(m);
      return s[w+t[0]:w+t[1]:t[2]];
    return int(s[w+z]);

  def __setitem__(self,key,b) :
    """Set the keyth bit of plane self to b, addressed as x,z
    If z is a slice, b should be a bitstring"""
    x,z = key;
    s = self.x;
    m = s._l//5;
    w = m*x;
    if isinstance(z,slice) :
      t = z.indices(m);
      s[w+t[0]:w+t[1]:t[2]] = b;
    else :
      s[w+z] = b;

  def __xor__(self,other) :
    """Bitwise xor other to self, both planes; left plane is munged!"""
    try :
      self.x ^= other.x;
      return self;
    except Exception :
      return NotImplemented;

################################################################
# SHA3

def theta(A) :
  C = A.plane(0) ^ A.plane(1) ^ A.plane(2) ^ A.plane(3) ^ A.plane(4);
  for x in xrange(5) :
    Dx = C[(x-1)%5,:]^(C[(x+1)%5,:]>>1);
    for y in xrange(5) :
      A[x,y,:] ^= Dx;
  return A;

def rho(A) :
  Z = sharray(A);
  x,y = 1,0;
  for t in xrange(24) :
    Z[x,y,:] = A[x,y,:]>>((t+1)*(t+2)//2);
    x,y = y,(2*x+3*y)%5;
  return Z;

def pi(A) :
  Z = sharray(A);
  for x in xrange(5) :
    for y in xrange(5) :
      Z[x,y,:] = A[(x+3*y)%5,x,:];
  return Z;

def chi(A) :
  Z = sharray(A);
  for x in xrange(5) :
    for y in xrange(5) :
      Z[x,y,:] ^= ~A[(x+1)%5,y,:] & A[(x+2)%5,y,:];
  return Z;

rc = 1;
R = 0x80;
for i in xrange(255) :
  R = (R^((R&1)*0x11c)) >> 1;
  rc = (rc << 1) | (R>>7);

def iota(A,i) :    # i is the round number
  w = A.x._l//25;
  l = rlog2(w);
  Z = sharray(A);
  RC = bitstring(0,w);
  for j in xrange(l+1) :
    RC[(1<<j)-1] = (rc >> (255-(j+7*i)%255))&1;
  Z[0,0,:] ^= RC;
  return Z;

def Rnd(A,i) :    # i is the round number
  return iota(chi(pi(rho(theta(A)))),i)

# inverse permutations:

iiota = iota

def ichi(A) :
  for i in xrange(3) :
    A = chi(A)
  return A;

def ipi(A) :
  Z = sharray(A);
  for x in xrange(5) :
    for y in xrange(5) :
      Z[(x+3*y)%5,x,:] = A[x,y,:];
  return Z;

def irho(A) :
  Z = sharray(A);
  x,y = 1,0;
  for t in xrange(24) :
    Z[x,y,:] = A[x,y,:]<<((t+1)*(t+2)//2);
    x,y = y,(2*x+3*y)%5;
  return Z;

def itheta(A) :
  for i in xrange(3*A.x._l//25-1) :
    A = theta(A);
  return A;

def iRnd(A,i) :
  return itheta(irho(ipi(ichi(iiota(A,i)))));

def Keccak_p(b,n) :    # b bit strings, n rounds
  w = b//25;
  l = rlog2(w);
  def X(S) :    # S is a b-bit string
    A = sharray(S);
    for i in xrange(12+2*l-n,12+2*l) :
      A = Rnd(A,i);
    return A.x;
  return X;

def Keccak_f(b) :
  l = rlog2(b//25);
  def X(S) :
    return Keccak_p(b,12+l)(S);
  return X;

def SPONGE(f,b,pad,r) :    # f is function over b-bit strings, r is rate
  def X(N,d) :
    S = bitstring(0,b);
    for p in N.iconcat(pad(r,len(N))).split(r) :    # absorption
      S ^= p.itrunc(b);
      S = f(S);
    Z = S.trunc(r);    # squeezing
    while len(Z) < d :
      S = f(S);
      Z = Z.iconcat(S.trunc(r));
    return Z.itrunc(d);
  return X;

def Keccak(c) :
  return SPONGE(Keccak_p(1600,24),1600,pad10_1,1600-c);

def pad10_1(x,m) :
  j = (-m-2)%x;
  return bitstring((1<<(j+1))|1,j+2);

def SHA3(x) :
  def X(M) :
    return Keccak(2*x)(M.concat(0,1),x);
  return X;

def SHAKE(x) :
  def X(M,d) :
    return Keccak(2*x)(M.concat(bitstring(0xf,4)),d);
  return X;

def RawSHAKE(x) :
  def X(J,d) :
    return Keccak(2*x)(J.concat(bitstring(3,2),d));
  return X;

def SPONGEN(f,b,pad,r) :    # returns a generator of r-bit strings
  def X(N) :
    S = bitstring(0,b);
    for p in N.iconcat(pad(r,len(N))).split(r) :    # absorption
      S ^= p.itrunc(b);
      S = f(S);
    while True :    # squeezing
      yield S.trunc(r);
      S = f(S);
  return X;

def KeccakN(c) :
  return SPONGEN(Keccak_p(1600,24),1600,pad10_1,1600-c);

def SHAKEN(x) :
  def X(M) :
    return KeccakN(2*x)(M.concat(bitstring(0xf,4)));
  return X;

_x3 = [bitstring(i,8)[::-1] for i in xrange(1<<8)];    # reverse 8 bits
_x3x = lambda x: _x3[int(x)];

def b3x(b) :
  """transform string-based bitstring for sha3 input/output"""
  return type(b).concat(*map(_x3x,b.split(8))).itrunc(b._l) if b._l else type(b)();

SHA3_224 = SHA3(224);
SHA3_256 = SHA3(256);
SHA3_384 = SHA3(384);
SHA3_512 = SHA3(512);

SHAKE128 = SHAKE(128);
SHAKE256 = SHAKE(256);

SHAKEN128 = SHAKEN(128);
SHAKEN256 = SHAKEN(256);
