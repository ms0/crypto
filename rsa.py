# RSA operations:
# create
# encrypt
# decrypt

from rational import gcd, sqrt
from ffield import isprime, bit_length

try:
  randrange
except :
  from random import randrange

try:
  xrange
except :
  xrange = range

def xgcd(x,y) :
  """Return g,c,d where g=cx+dy is the gcd of x and y"""
  u0,v0,u1,v1 = 1,0,0,1;
  while y :
    q,r= divmod(x,y);
    x,u0,v0,y,u1,v1 = y,u1,v1,r,u0-q*u1,v0-q*v1;
  return x,u0,v0;

def prime_in_range(a,b) :
  """Return a random odd prime in the interval [a|1,b|1)"""
  while True :
    p = randrange(a|1,b|1,2);
    if isprime(p) :
      return p;

class RSA() :
  """RSA class
Instance variables:
  n: the RSA modulus, the product of two primes
  e: the RSA public key
  _d: the RSA private key
Methods:
  __init__, encrypt, decrypt"""

  def __init__(self,m,e=1+(1<<16)) :
    """Create an RSA modulus < m; try to use suggested public key e; compute private key"""
    if bit_length(m) < 32 :
      raise ValueError('max modulus too small');
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
    """Return encrypted m"""
    return pow(m,self.e,self.n);

  def decrypt(self,m) :
    """Return decrypted m"""
    return pow(m,self._d,self.n);
