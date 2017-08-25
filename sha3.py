# SHA-3 implementation

from bitstring import *

def theta(A) :
  C = A.plane(0) ^ A.plane(1) ^ A.plane(2) ^ A.plane(3) ^ A.plane(4);
  D = plane(C.x);
  w = A.x.w;    # lane size
  for x in range(5) :
    for z in range(w) :
      D[x,z] = C[(x-1)%5,z] ^ C[(x+1)%5,(z-1)%w];
  for x in range(5) :
    for y in range(5) :
      for z in range(w) :
        A[x,y,z] ^= D[x,z];
  return A;

def rho(A) :
  w = A.x.w;
  Z = sharray(A.x);
  x,y = 1,0;
  for t in range(24) :
    for z in range(w) :
      Z[x,y,z] = A[x,y,(z-(t+1)*(t+2)//2)%w];
    x,y = y,(2*x+3*y)%5;
  return Z;

def pi(A) :
  w = A.x.w;
  Z = sharray(A.x);
  for x in range(5) :
    for y in range(5) :
      for z in range(w) :
        Z[x,y,z] = A[(x+3*y)%5,x,z];
  return Z;

def chi(A) :
  Z = sharray(A.x);
  for x in range(5) :
    for y in range(5) :
      for z in range(A.x.w) :
        Z[x,y,z] ^= (A[(x+1)%5,y,z] ^ 1) & A[(x+2)%5,y,z];
  return Z;

rc = 1;
R = 0x80;
for i in xrange(255) :
  R ^= (R&1)*0x11c;
  R >>= 1;
  rc = (rc << 1) | (R>>7);

def iota(A,i) :    # i is the round number
  w = A.x.w;
  l = rlog2(w);
  Z = sharray(A.x);
  RC = bitstring(0,w);
  for j in range(l+1) :
    RC[(1<<j)-1] = (rc >> (255-(j+7*i)%255))&1;
  for z in range(w) :
    Z[0,0,z] ^= RC[z];
  return Z;

def Rnd(A,i) :    # i is the round number
  return iota(chi(pi(rho(theta(A)))),i)

def Keccak_p(b,n) :    # b bit strings, n rounds
  w = b//25;
  l = rlog2(w);
  def X(S) :    # S is a b-bit string
    A = sharray(S);
    for i in range(12+2*l-n,12+2*l) :
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
    P = N.concat(pad(r,len(N)));
    n = len(P)//r;
    c = b-r;
    S = bitstring(0,b);
    for i in range(n) :
      S = f(S^P[i*r:(i+1)*r].concat(bitstring(0,c)));
    Z = S.trunc(r);
    while len(Z) < d :
      S = f(S);
      Z = Z.concat(S.trunc(r));
    return Z.trunc(d);
  return X;

def Keccak(c) :
  def X(N,d) :
    return SPONGE(Keccak_p(1600,24),1600,pad10_1,1600-c)(N,d);
  return X;

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
  return X

def RawSHAKE(x) :
  def X(J,d) :
    return Keccak(2*x)(J.concat(bitstring(3,2),d));
  return X;

SHA3_224 = SHA3(224);
SHA3_256 = SHA3(256);
SHA3_384 = SHA3(384);
SHA3_512 = SHA3(512);

SHAKE128 = SHAKE(128);
SHAKE256 = SHAKE(256);
