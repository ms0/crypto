# RSA operations:
# create
# encrypt
# decrypt

from msmath.rational import sqrt
from msmath.conversions import gcd, bit_length, xrange
from msmath.numfuns import isprime

try:
  randrange
except Exception :
  from random import randrange

def xgcd(a,b) :
  """Return g,c,d where g=ca+db is the gcd of a and b"""
  c,d,e,f = 1,0,0,1;
  while b :
    q,r= divmod(a,b);
    a,c,d,b,e,f = b,e,f,r,c-q*e,d-q*f;
  return (-a,-c,-d) if a < 0 else (a,c,d);

def prime_in_range(a,b) :
  """Return a random odd prime in the interval [a|1,b|1)"""
  while True :
    p = randrange(a|1,b|1,2);
    if isprime(p) :
      return p;

class RSA(object) :
  """RSA class
Instance variables:
  n: the RSA modulus, the product of two primes
  e: the RSA public key
  _d: the RSA private key
Methods:
  __init__, encrypt, decrypt
Properties:
  _pq"""

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
      p *= q//gcd(p,q);    # reduced totient
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

  @property
  def _pq(self) :
    """From public and private keys, compute and return (p,q)"""
    de1 = self._d*self.e-1;    # multiple of reduced totient
    de1 //= de1&-de1;    # maximal odd divisor of same
    for g in xrange(2,self.n) :    # find a square root of 1 neither 1 nor -1
      gg = gcd(g,self.n);
      if gg != 1 :
        return (gg,self.n//gg);
      g = pow(g,de1,self.n);
      if g == 1 or g == self.n-1 :
        continue;
      while True :
        g2 = pow(g,2,self.n);
        if g2 == 1 :
          g = gcd(g-1,self.n);
          return (g,self.n//g);
        elif g2 == self.n-1 :
          break;
        g = g2;
