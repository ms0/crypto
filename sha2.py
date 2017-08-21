# SHA1 and 2

from bitstring import *

nprimes = 80;
from rational import *
from ffield import isprime

def primes() :
  yield 2;
  p = 3;
  while True :
    if isprime(p) : yield p;
    p += 2;

p = primes();
P = [next(p) for i in range(nprimes)]

def froot(x,r,b) :    # r is which root, b is number of fraction bits
  return int(rational(x<<(r*b))**rational(1,r))%(1<<b);

fsqrt = lambda x,b: froot(x,2,b);
fcbrt = lambda x,b: froot(x,3,b);

def printhex(a,b) :    # a is array of b-bit numbers
  w = 256/b;  # words per line
  for i in range(0,len(a),w) :
    print(' '.join('%%0%dx'%(b//4)%(a[i+j]) for j in range(w)));

def pad(M,      # message (as bitstring)
        L=None, # number of bits in max message length
        m=None  # blocksize
       ) :
  L = L or 64;
  m = m or 8*L;
  k = (-1-len(M)-L)%m;
  return M.concat(bitstring(1<<k,k+1)).concat(bitstring(len(M),L));

def split(M,w) :    # split padded message M into words with wordsize w
  return [M[i:i+w] for i in xrange(0,len(M),w)];

def concat(H) :
  x = bitstring();
  for h in H :
    x = x.concat(h);
  return x;

################################################################
# SHA1
    
Ch = lambda x,y,z: x&y|~x&z;
Parity = lambda x,y,z: x^y^z;
Maj = lambda x,y,z: x&y|y&z|z&x;

SHA1f = lambda t,x,y,z : Ch(x,y,z) if 0<=t<20 else Maj(x,y,z) if 40<=t<60 else Parity(x,y,z);

K1 = map(lambda x: int(rational(x<<60)**rational(1,2)), (2,3,5,10));
SHA1K = lambda t: K1[t//20];

H1 = [0x67452301,0xefcdab89,0x98badcfe,0x10325476,0xc3d2e1f0];

def SHA1(M) :
  m = 512;    # blocksize
  w = 32;     # wordsize
  wpb = m//w;
  M = split(pad(M),w);
  N = len(M)//wpb;
  H = map(lambda x: bitstring(x,w),H1);
  for i in xrange(N) :
    Mi = M[i*wpb:(i+1)*wpb];
    W = Mi[0:16];
    for t in xrange(16,80) :
      W.append((W[t-3]^W[t-8]^W[t-14]^W[t-16])<<1);
    v = [H[j] for j in xrange(5)];
    for t in xrange(80) :
      v[:] = [(v[0]<<5)+SHA1f(t,*v[1:4])+v[4]+SHA1K(t)+W[t], v[0], v[1]>>2] + v[2:4];
    for j in xrange(5) :
      H[j] += v[j];
  return concat(H);

################################################################
# SHA2
      
K2 = map(lambda x: fcbrt(x,64),P[:80]);

H256 = map(lambda x: fsqrt(x,32),P[:8]);
H384 = map(lambda x: fsqrt(x,64),P[8:16]);
H512 = map(lambda x: fsqrt(x,64),P[:8]);
H224 = map(lambda x: x%(1<<32),H384);    # low order 32 bits of H384!
      
S320 = lambda x : (x>>2)^(x>>13)^(x>>22);
S321 = lambda x : (x>>6)^(x>>11)^(x>>25);
s320 = lambda x : (x>>7)^(x>>18)^((x&~7)>>3);
s321 = lambda x : (x>>17)^(x>>19)^((x&~0x3ff)>>10);
      
S640 = lambda x : (x>>28)^(x>>34)^(x>>39);
S641 = lambda x : (x>>14)^(x>>18)^(x>>41);
s640 = lambda x : (x>>1)^(x>>8)^((x&~0x7f)>>7);
s641 = lambda x : (x>>19)^(x>>61)^((x&~0x3f)>>6);

SHA224 = lambda M: SHA256(M,H224).trunc(224);

def SHA2(M,H0,m,w,n,S0,S1,s0,s1) :
  wpb = m//w;
  K = map(lambda x: x >> (64-w), K2[:n]);
  M = split(pad(M,2*w),w);
  N = len(M)//wpb;
  H = map(lambda x: bitstring(x,w), H0);
  for i in xrange(N) :
    Mi = M[i*wpb:(i+1)*wpb];
    W = Mi[0:16];
    for t in xrange(16,n) :
      W.append(s1(W[t-2])+W[t-7]+s0(W[t-15])+W[t-16]);
    v = [H[j] for j in xrange(8)];
    for t in xrange(n) :
      T1 = v[7]+S1(v[4])+Ch(*v[4:7])+K[t]+W[t];
      T2 = S0(v[0])+Maj(*v[0:3]);
      v[:] = [T1+T2]+v[0:3]+[v[3]+T1]+v[4:7];
    for j in xrange(8) :
      H[j] += v[j];
  return concat(H);

def SHA256(M,H0=H256) :
  return SHA2(M,H0,512,32,64,S320,S321,s320,s321);

SHA384 = lambda M: SHA512(M,H384).trunc(384);
      
def SHA512(M,H0=H512) :
  return SHA2(M,H0,1024,64,80,S640,S641,s640,s641);

def SHA512t(t,M) :
  if (not 0<t<512 or t==384) :
    raise valueError('t must be a positive integer < 512 and not 384');
  return SHA512(M,map(
      lambda x:x.x,
      split(SHA512(bitstring('SHA-512/%d'%(t)),
                   map(lambda x: x^0xa5a5a5a5a5a5a5a5, H512)),64))).trunc(t);

SHA512_224 = lambda M: SHA512t(224,M);
SHA512_256 = lambda M: SHA512t(256,M);
