# big-endian version

import sys

if sys.version_info[0] < 3 :

  def isint(x) :
    """Return True iff an integer"""
    return isinstance(x,(int,long));

else :

  def isint(x) :
    """Return True iff an integer"""
    return isinstance(x,int);

  xrange = range;

from math import log

rlog2 = lambda x: int(round(log(x,2)));
is2power = lambda x: x&-x == x;

################################################################

# how do we compare strings of different lengths???
# .x is bitstring interpreted as big-endian unsigned binary number
# ._l or .b is number of bits
# if ._l is 25 times an integral power of 2:
#   .w is b/25 [lane size]
#   .l is log2(w)
# [i] is ith bit where [0] is the leftmost bit
# [i:j] is ith to jth bit, as (j-i) length bitstring
# conversion to array by sharray(bitstring)


class bitstring(object) :

  def __init__(self,*args) :
    if not args :
      args = 0,0;
    if len(args) == 1 :
      if isinstance(args[0], str) :
        args = (s2bs(args[0]),);
      if isinstance(args[0], bitstring) :
        args = args[0].x, args[0]._l;    # make a copy
      else : raise TypeError('single arg must be bitstring')
    if len(args) > 2 :
      raise TypeError('too many args');
    x,l = args;
    if not isint(x) :
      raise TypeError('value must be integer');
    if not isint(l) or l < 0 :
      raise TypeError('length must be nonnegative');
    self._l = l;    # number of bits
    self.x = x & ((1<<l)-1);

  def __int__(self) :
    return self.x;

  def __repr__(self) :
    return '0x%%0%dx'%((self._l+3)//4)%(self.x);

  def __str__(self) :
    return '%%0%dx'%((self._l+3)//4)%(self.x);

  def __len__(self) :
    return self._l;

  def __bool__(self) :
    return not not self.x;

  __nonzero__ = __bool__

  def __eq__(self,other) :
    if type(self) != type(other) or self._l != other._l :
      raise TypeError('not bitstring');
    return self.x == other.x;

  def __ne__(self,other) :
    if type(self) != type(other) or self._l != other._l :
      raise TypeError('not bitstring');
    return self.x != other.x;

  def __gt__(self,other) :
    if type(self) != type(other) or self._l != other._l :
      raise TypeError('not bitstring');
    return self.x > other.x;

  def __ge__(self,other) :
    if type(self) != type(other) or self._l != other._l :
      raise TypeError('not bitstring');
    return self.x >= other.x;

  def __le__(self,other) :
    if type(self) != type(other) or self._l != other._l :
      raise TypeError('not bitstring');
    return self.x <= other.x;

  def __lt__(self,other) :
    if type(self) != type(other) or self._l != other._l :
      raise TypeError('not bitstring');
    return self.x < other.x;

  def __invert__(self) :
    return bitstring(~self.x,self._l);

  def __neg__(self) :
    return bitstring(-self.x,self._l);

  def __ilshift__(self,n) :    # actually, rotate
    if not isint(n) :
      return NotImplemented;
    n = n%self._l;
    if n < 0 : n += self._l;
    self.x = (self.x<<n)|(self.x>>(self._l-n));
    return self;

  def __lshift__(self,n) :
    return bitstring(self).__ilshift__(n);

  def __irshift__(self,n) :    # actually, rotate
    if not isint(n) :
      return NotImplemented;
    n = n%self._l;
    if n < 0 : n += self._l;
    self.x = (self.x>>n)|(self.x<<(self._l-n));
    return self;

  def __rshift__(self,n) :
    return bitstring(self).__irshift__(n);

  def __ixor__(self,other) :
    if isint(other) and -1 <= other>>self._l <= 0 :
      return bitstring(self.x^other, self._l);
    if type(self) != type(other) or self._l != other._l :
      return NotImplemented;
    self.x ^= other.x;
    return self;

  def __xor__(self,other) :
    return bitstring(self).__ixor__(other);

  __rxor__ = __xor__

  def __iand__(self,other) :
    if isint(other) and -1 <= other>>self._l <= 0 :
      self.x &= other;
    elif type(self) == type(other) and self._l == other._l :
      self.x &= other.x;
    else :
      return NotImplemented;
    return self;

  def __and__(self,other) :
    return bitstring(self).__iand__(other);

  __rand__ = __and__

  def __ior__(self,other) :
    if isint(other) and -1 <= other>>self._l <= 0 :
      self.x |= other;
    elif type(self) == type(other) and self._l == other._l :
      self.x |= other.x;
    else :
      return NotImplemented;
    return self;

  def __or__(self,other) :
    return bitstring(self).__ior__(other);

  __ror__ = __or__

  def __iadd__(self,other) :
    if isint(other) and -1 <= other>>self._l <= 0 :
      self.x += other;
    elif type(self) == type(other) and self._l == other._l :
      self.x += other.x;
    else :
      return NotImplemented;
    return self;

  def __add__(self,other) :
    return bitstring(self).__iadd__(other);

  __radd__ = __add__

  def __isub__(self,other) :
    if isint(other) and -1 <= other>>self._l <= 0 :
      self.x -= other;
    elif type(self) == type(other) and self._l == other._l :
      self.x -= other.x;
    else :
      return NotImplemented;
    return self;

  def __sub__(self,other) :
    return bitstring(self).__isub__(other);

  def __rsub__(self,other) :
    if isint(other) and -1 <= other>>self._l <= 0 :
      return bitstring(other-self.x, self._l);
    return NotImplemented;
    

  def __getitem__(self,key) :
    if not isinstance(key,tuple) :
      key = (key,);
    x = 0;
    l = 0;
    for k in key :
      if isint(k) :
        if -self._l <= k < self._l :
          x = (x<<1) | ((self.x>>(-1-k if k < 0 else (self._l-1-k)))&1);
          l += 1;
        else :
          raise IndexError('bitstring index out of range');
      elif isinstance(k,slice) :    # should optimize for step==1
        for k in xrange(*k.indices(self._l)) :
          x = (x<<1) | ((self.x>>(self._l-1-k))&1);
          l += 1;
      else :
        raise TypeError('bitstring index not int or slice');
    return bitstring(x,l);

  def __setitem__(self,key,value) :    # this makes bitstring mutable!
    if not isinstance(key,tuple) :
      key = (key,);
    l = 0;
    for k in key :
      if isint(k) :
        if -self._l <= k < self._l :
          l += 1;
        else :
          raise IndexError('bitstring index out of range');
      elif isinstance(k,slice) :
        start,stop,step = k.indices(self._l);
        l += max(0,(stop-start+step-(1 if step>0 else -1)))//step;
      else :
        raise TypeError('bitstring index not int or slice');
    if isinstance(value,bitstring) :
      if value._l != l :
        raise TypeError('value wrong size');
      value = value.x;
    elif isint(value) :
      if value >= 1<<l :
        raise TypeError('value too big');
    else :
      raise TypeError('value not bitstring or int');
    b = 1<<(self._l-1);
    for k in key :
      if isint(k) :
        l -= 1;
        if k<0 : k += self._l;
        self.x = self.x|(b>>k) if value&(1<<l) else self.x&~(b>>k);
      elif isinstance(k,slice) :    # should optimize for step==1
        for k in xrange(*k.indices(self._l)) :
          l -= 1;
          self.x = self.x|(b>>k) if value&(1<<l) else self.x&~(b>>k);
      
  def concat(self,*others) :
    bs = self.x;
    ls = self._l;
    for other in others :
      if isint(other) and 0 <= other <= 1 :
        bs = (bs<<1) | other;
        ls += 1;
      elif type(self) == type(other) :
        bs = (bs<<other._l) | other.x;
        ls += other._l;
      else :
        raise TypeError('not bitstring');
    return bitstring(bs,ls);

  def tacnoc(self,*others) :    # concatenate backwards
    bs = self.x;
    ls = self._l;
    for other in others :
      if isint(other) and 0 <= other <= 1 :
        bs |= other<<ls;
        ls += 1;
      elif type(self) == type(other) :
        bs |= other.x<<ls;
        ls += other._l;
      else :
        raise TypeError('not bitstring');
    return bitstring(bs,ls);
        
  def trunc(self,l) :
    if not isint(l) or l < 0 :
      raise IndexError('length not nonnegative integer');
    if l > self._l :
      raise IndexError('bitstring too short');
    return bitstring(self.x>>(self._l-l),l);

  def __mul__(self,n) :
    if not isint(n) or n < 0 :
      raise IndexError('repetition not nonnegative integer');
    x = 0;
    for i in xrange(n) :
      x = (x<<self._l) | self.x;
    return bitstring(x,n*self._l);

  def __getattr__(self,name) :
    if not self._l%25 and is2power(self._l//25) :
      if name == 'b' :
        return self._l;
      if name == 'w' :
        return self._l//25;
      if name == 'l' :
        return rlog2(self._l//25);
    raise AttributeError('bitstring has no attribute '+name);

################################################################

# sha3 array
# a.x is bitstring for array
# a[x,y,z] is a bit that can be read and set
# a.plane(i)

class sharray(object) :
  def __init__(self,*args) :
    if len(args) == 0 :
      args = (0,0);
    elif len(args) == 1 :    # copy a sharray or bitstring to a state array
      if isinstance(args[0],bitstring) and not args[0]._l%25 and is2power(args[0]._l//25) :
        args = args[0].x, args[0].l;
      elif isinstance(args[0],sharray) :
        args = args[0].x.x, args[0].x.l;
      else :
        raise TypeError('single arg not bitstring of compatible length');
    if len(args) == 2 :  # convert a binary number and z length to a state array
      if not isint(args[0]) :
        raise TypeError('value must be integer');
      if not isint(args[1]) or args[1] < 0 :
        raise TypeError('l must be positive integer');
      self.x = bitstring(args[0],25<<args[1]);
    else :
      raise TypeError('too many args');

  def __str__(self) :
    return str(self.x);

  def __repr__(self) :
    return repr(self.x);

  def __getitem__(self,key) :
    x,y,z = key;
    if 0 <= x < 5 and 0 <= y < 5 and 0 <= z < self.x.w :
      return self.x[self.x._l//25*(5*y+x)+z];
    raise IndexError('sharray index out of range');

  def __setitem__(self,key,b) :
    x,y,z = key;
    if 0 <= x < 5 and 0 <= y < 5 and 0 <= z < self.x.w :
      self.x[self.x._l//25*(5*y+x)+z] = b;
    else :
      raise IndexError('sharray index out of range');

  def plane(self,i) :
    p = self.x._l//5;
    io = p*i;
    return _plane(self.x[io:io+p]);

def c2bs(c) :
  return bitstring(ord(c),8);

def s2bs(s) :
  b = bitstring();
  for c in s :
    b = b.concat(c2bs(c));
  return b;

def b3x(b) :     # convert bitstream to bitstream for sha3 input/output
  l = b._l;
  c = bitstring();
  for i in xrange(0,l+7,8) :
    c = c.concat(b[i+7:i-1 if i else None:-1]);
  return c;

################################################################
# sha3 plane
# .x is bitstring for plane
# [x,z] can be read and set

class plane(object) :
  def __init__(self,*args) :
    if len(args) == 1 :
      if isinstance(args[0],bitstring) and not args[0]._l%5 and is2power(args[0]._l//5) :
        args = args[0].x, rlog2(args[0]._l//5);
      elif isinstance(args[0],int) :
        args = 0,args[0];
      else :
        raise TypeError('single arg not bitstring of compatible length');
    if len(args) == 2 :
      if not isint(args[0]) :
        raise TypeError('value must be integer');
      if not isint(args[1]) or args[1] < 0 :
        raise TypeError('l must be positive integer');
      self.x = bitstring(args[0],5<<args[1]);
    else :
      raise TypeError('too many args');

  def __str__(self) :
    return str(self.x);

  def __repr__(self) :
    return repr(self.x);

  def __getitem__(self,key) :
    x,z = key;
    if 0 <= z < self.x._l//5 :
      return self.x[self.x._l//5*x+z];
    raise IndexError('index out of range');

  def __setitem__(self,key,b) :
    x,z = key;
    if 0 <= z < self.x._l//5 :
      self.x[self.x._l//5*x+z] = b;
    else :
      raise IndexError('index out of range');

  def __xor__(self,other) :
    if type(self) != type(other) :
      raise TypeError('not plane');
    return plane(self.x^other.x);

_plane = plane
