# RSA operations:
# create
# encrypt
# decrypt

from rational import gcd, sqrt, xrange
from ffield import isprime, bit_length

try:
  randrange
except :
  from random import randrange

def xgcd(x,y) :
  u0,v0,u1,v1 = 1,0,0,1;
  while y :
    q = x//y;
    x,u0,v0,y,u1,v1 = y,u1,v1,x-q*y,u0-q*u1,v0-q*v1;
  return x,u0,v0;

def prime_in_range(a,b) :
  while True :
    p = randrange(a|1,b|1,2);
    if isprime(p) :
      return p;

class RSA() :

  def __init__(self,m,e=1+(1<<16)) :
    # m is maximum modulus (m/2 <= n < m)
    if bit_length(m) < 32 :
      raise ValueError('modulus too small');
    s = int(sqrt(m<<7));
    while True :
      p = prime_in_range(s>>1,s);
      r = m//p;
      q = prime_in_range(r>>1,r);
      n = p*q;
      p -= 1;
      q -= 1;
      p *= q//gcd(p,q);    # Carmichael totient
      k = randrange(1,n);
      if pow(k,p,n) != 1 :
        continue;    # p or q not prime
      for x in xrange(e,p) :
        g,c,d = xgcd(p,x);
        if g == 1 :    # e prime to phi
          break;
      else :
        continue;    # no exponent works?
      break;
    self.n = n;
    self.e = x;
    self._d = d%p;

  def encrypt(self,m) :
    return pow(m,self.e,self.n);

  def decrypt(self,m) :
    return pow(m,self._d,self.n);
