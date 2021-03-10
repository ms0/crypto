""" bitstring classes """

__all__ = ['bitstrings']

# big-endian version implemented with list of ints

import sys

if sys.version_info[0] < 3 :

  def isint(x) :
    """Return True iff an integer"""
    return isinstance(x,(int,long));

  lmap = map;
  
else :

  def isint(x) :
    """Return True iff an integer"""
    return isinstance(x,int);

  def lmap(f,*x) :
    """Return list(map(f,*x))"""
    return list(map(f,*x));

  xrange = range;

try :
  int.bit_length;
  bit_length = lambda n : n.bit_length();
except Exception :
  import math
  def bit_length(n) :
    n = abs(n);
    b = 0;
    while n :
      try :
        l = int(math.log(n,2));
        while n >> l : l += 1;
      except OverflowError :
        l = sys.float_info.max_exp-1;
      b += l
      n >>= l;
    return b;

inf = float('inf');

def chunkify(x,l,B) :
  """return a list of B-sized chunks for int x of length l"""
  n = (l+B-1)//B;    # number of B-chunks
  y = [0]*n;
  y[-1] = x << ((B-l)%B);
  kf = 0 if B > 128 else bit_length(256//B-1);
  for k in xrange(bit_length(n-1),kf,-1) :
    c = 1<<(k-1);    # chunk increment
    s = c*B;         # size of chunks being created
    m = (1<<s)-1;    # mask
    for i in xrange(n-1,c-1 if (n//c)&1 else -1,-c<<1) :
      y[i-c] = y[i] >> s;
      y[i] &= m;
  if kf :
    m = (1<<B)-1;
    for i in xrange(n-1,-1,-1<<kf) :
      x = y[i];
      while x :
        y[i] = x&m;
        x >>= B;
        i -= 1;
  return y;

def _fill(self,x,mustzero=True) :
  """fill list self._x with value x of bitlength l"""
  B = self._B;
  l = self._l;
  v = self._x;
  l %= B;
  if l : x <<= (B-l);
  m = (1<<B)-1;
  i = -1;
  while x :
    v[i] = x&m;
    x >>= B;
    i -= 1;
  if mustzero :
    i += len(v);
    for i in xrange(0,i+1) :
      v[i] = 0;

def _filll(self,x) :
  """or value x into list self._x"""
  B = self._B;
  l = self._l;
  v = self._x;
  l %= B;
  if l : x <<= (B-l);
  m = (1<<B)-1;
  i = -1;
  while x :
    v[i] |= x&m;
    x >>= B;
    i -= 1;

def _fillr(self,b,other) :
  """fill list self._x starting at bit b, with other"""
  x = self._x;
  y = other._x;
  B = self._B;
  C = other._B;
  m = (1<<B)-1;
  if B == C :
    bb,b = divmod(b,B);
    if b :
      c = B-b;
      z = (self._l-1)//B;    # last chunk
      for i,y in enumerate(y,bb) :
        x[i] |= y>>b;
        if i < z : x[i+1] = (y<<c)&m;
    else :
      x[bb:] = y;
  else :
    try :
      for i,y in enumerate(y) :    # C-bit chunks
        sb,sr = divmod(b,B);
        eb,er = divmod(b+C-1,B);
        if sb==eb :
          x[sb] |= y<<(B-1-er);
        else :
          x[sb] |= y>>(C-B+sr);
          for a in xrange(sb+1,eb+1) :
            n = (a-sb+1)*B-C-sr;
            x[a] |= (y<<n if n >= 0 else y>>-n)&m;
        b += C;
    except IndexError:
      pass;
    x[-1] &= -1<<(-self._l%B);


################################################################

# ._l is number of bits (also len())
# [i] is ith bit where [0] is the leftmost bit as a length-1 bitstring
# slice indexing is also allowed, again by bit
# a comma-separated sequence of indices produces a bitstring which is
#  the left-to-right concatenation of the bitstrings for each index
# ._x is internal representation as either an int or a list of ints
# ._B is the maximum number of bits in each of those ints
# only the last (or only) int can hold fewer than _B bits
# if ._x is an int, the lsb is the rightmost bit of the string
# if ._x is a list, the rightmost bit of the bitstring is
#   (._x[-1]>>(._B-1-._l%._B))&1

def __init__(self,*args) :
  """Create a bitstring from an int and a length, or from another bitstring"""
  if not args :
    self._x = self._l = 0;
    return;
  B = self._B;
  if len(args) == 1 :
    a = args[0];
    if isinstance(a,type(self)) :
      self._l = l = a._l;
      self._x = a._x[:] if l > B else a._x;
      return;
    if isinstance(a, str) :
      if B == 8 :
        self._l = l = len(a)<<3;
        self._x = lmap(ord,a);
        if l <= B : self._x = l and self._x[0];
        return;
      else :
        a = _bitstring[8](a);
    if isinstance(type(a),bitstrings) :
      self._x = self._l = 0;
      __iconcat__(self,a);
      return;
    else : raise TypeError('single arg must be bitstring')
  if len(args) > 2 :
    raise TypeError('too many args');
  x,l = args;
  if not isint(x) :
    raise TypeError('value must be integer');
  if not isint(l) or l < 0 :
    raise TypeError('length must be nonnegative');
  x &= (1<<l)-1;
  self._l = l;    # number of bits
  if l <= B :
    self._x = x;
  else :
    self._x = chunkify(x,l,B);

def __copy__(self) :
  """Return a copy of self"""
  return type(self)(self);

def __int__(self) :
  """Return the int that is the big-endian interpretation of the bitstring"""
  B = self._B;
  l = self._l;
  if l <= B :
    return self._x;
  z = (B-l)%B;    # number of zeroes at end
  x = self._x;
  n = len(x);    # at least 2
  o = 256//B;
  if o > 1 :
    y = [];
    for k in xrange(n%o,n+o-1,o) :
      n = 0;
      for i in xrange(max(0,k-o),k) :
        n = (n<<B) | x[i];
      y.append(n);
    n = len(y);
    x = y;
    B = o*B;
  while n > 1 :
    if n&1 :
      y = x[:1];
      r = xrange(1,n,2);
    else :
      y = [];
      r = xrange(0,n,2);
    for i in r :
      y.append((x[i]<<B)|x[i+1]);
    B <<= 1;
    n = len(y);
    x = y;
  return y[0]>>z;

def __repr__(self) :
  """Return a string representing the bitstring"""
  return '%s(0x%%0%dx,%d)'%(type(self).__name__,(self._l+3)//4,self._l)%(int(self));

def __str__(self) :
  """Return a string representing the bitstring"""
  return '%%0%dx'%((self._l+3)//4)%(int(self));

def __len__(self) :
  """Return the length of the bitstring"""
  return self._l;

def __bool__(self) :
  """Return True unless the bitstring has length 0"""
  return not not self._l;

__nonzero__ = __bool__

def __eq__(self,other) :
  """Return True iff self and other are the same bitstring"""
  if type(type(self)) != type(type(other)) :
    return NotImplemented;
  return self._l == other._l and (
    self._x == other._x if self._B == other._B else int(self) == int(other));

def __ne__(self,other) :
  """Return True iff self and other are not the same bitstring"""
  if type(type(self)) != type(type(other)) :
    return NotImplemented;
  return self._l != other._l or (
    self._x != other._x if self._B == other._B else int(self) != int(other));

def __lt__(self,other) :
  """Return True iff self is a proper initial substring of other"""
  if type(type(self)) != type(type(other)) :
    return NotImplemented;
  return self._l < other._l and self == other[0:self._l];

def __le__(self,other) :
  """Return True iff self is an initial substring of other"""
  if type(type(self)) != type(type(other)) :
    return NotImplemented;
  return self._l <= other._l and self == other[0:self._l];

def __ge__(self,other) :
  """Return True iff other is an initial substring of self"""
  if type(type(self)) != type(type(other)) :
    return NotImplemented;
  return self._l >= other._l and self[:other._l] == other;

def __gt__(self,other) :
  """Return True iff other is a proper initial substring of self"""
  if type(type(self)) != type(type(other)) :
    return NotImplemented;
  return self._l > other._l and self[:other._l] == other;

def __invert__(self) :
  """Return the bitwise complement of self"""
  B = self._B;
  l = self._l;
  if l <= B :
    return type(self)(((1<<l)-1)-self._x,l);
  b = type(self)(0,l);
  v = b._x;
  l %= B;
  m = (1<<B)-1;
  for i,x in enumerate(self._x) :
    v[i] = m-x;
  if l : v[-1] ^= (1<<(B-l))-1;
  return b;

def __neg__(self) :
  """Return the two's complement of self"""
  return type(self)(-int(self),self._l);

def __pos__(self) :
  """Return self"""
  return self;

def __ilshift__(self,n) :    # actually, rotate
  """Rotate left self by n bits"""
  if not isint(n) :
    return NotImplemented;
  B = self._B;
  l = self._l;
  n %= l;
  if not n : return self;
  if l <= B :
    self._x = ((self._x<<n)|(self._x>>(l-n)))&((1<<l)-1);
  else :
    x = int(self);
    _fill(self,((x<<n)|(x>>(l-n)))&((1<<l)-1));
  return self;

def __lshift__(self,n) :
  """Return result of rotating self n bits left"""
  return __ilshift__(type(self)(self),n);

def __irshift__(self,n) :    # actually, rotate
  """Rotate right self by n bits"""
  if not isint(n) :
    return NotImplemented;
  B = self._B;
  l = self._l;
  n %= l;
  if not n : return self;
  if l <= B :
    self._x = ((self._x>>n)|(self._x<<(l-n)))&((1<<l)-1);
  else :
    x = int(self);
    _fill(self,((x>>n)|(x<<(l-n)))&((1<<l)-1));
  return self;

def __rshift__(self,n) :
  """Return result of rotating self n bits right"""
  return __irshift__(type(self)(self),n);

def __ixor__(self,other) :
  """Bitwise xor other to self"""
  B = self._B;
  l = self._l;
  x = self._x;
  if type(type(self)) == type(type(other)) and l == other._l :
    if l <= B :
      self._x ^= int(other);
      return self;
    if other._B == B :
      for i,o in enumerate(other._x) :
        x[i] ^= o;
      return self;
    other = int(other);
  if isint(other) and -1 <= other>>l <= 0 :
    other &= (1<<l)-1;
    if l <= B :
      self._x ^= other;
    else :
      l %= B;
      if l : other <<= (B-l);
      i = -1;
      m = (1<<B)-1;
      while other :
        x[i] ^= other&m;
        other >>= B;
        i -= 1;
    return self;
  return NotImplemented;

def __xor__(self,other) :
  """Return bitwise xor of self and other"""
  return __ixor__(type(self)(self),other);

__rxor__ = __xor__

def __iand__(self,other) :
  """Bitwise and other to self"""
  B = self._B;
  l = self._l;
  x = self._x;
  if type(type(self)) == type(type(other)) and l == other._l :
    if l <= B :
      self._x &= int(other);
      return self;
    if other._B == B :
      for i,o in enumerate(other._x) :
        x[i] &= o;
      return self;
    other = int(other);
  if isint(other) and -1 <= other>>l <= 0 :
    other &= (1<<l)-1;
    if l <= B :
      self._x &= other;
    else :
      l %= B;
      if l : other <<= (B-l);
      i = len(x)-1;
      while i >= 0 :
        x[i] &= other;
        other >>= B;
        i -= 1;
    return self;
  return NotImplemented;

def __and__(self,other) :
  """Return bitwise and of self and other"""
  return __iand__(type(self)(self),other);

__rand__ = __and__

def __ior__(self,other) :
  """Bitwise or other to self"""
  B = self._B;
  l = self._l;
  x = self._x;
  if type(type(self)) == type(type(other)) and l == other._l :
    if l <= B :
      self._x |= int(other);
      return self;
    if other._B == B :
      for i,o in enumerate(other._x) :
        x[i] |= o;
      return self;
    other = int(other);
  if isint(other) and -1 <= other>>l <= 0 :
    other &= (1<<l)-1;
    if l <= B :
      self._x |= other;
    else :
      l %= B;
      if l : other <<= (B-l);
      i = -1;
      m = (1<<B)-1;
      while other :
        x[i] |= other&m;
        other >>= B;
        i -= 1;
    return self;
  return NotImplemented;

def __or__(self,other) :
  """Return bitwise or of self and other"""
  return __ior__(type(self)(self),other);

__ror__ = __or__

def __iadd__(self,other) :
  """Add other to self, discard carry"""
  B = self._B;
  l = self._l;
  if type(type(self)) == type(type(other)) and l == other._l or \
     isint(other) and -1 <= other>>l <= 0 :
    if l <= B :
      self._x = (self._x+int(other))&((1<<l)-1);
    else :
      _fill(self,(int(self)+int(other))&((1<<l)-1));
    return self;
  return NotImplemented;

def __add__(self,other) :
  """Return sum of self and other, discarding carry"""
  return __iadd__(type(self)(self),other);

__radd__ = __add__

def __isub__(self,other) :
  """Subtract other from self, discarding carry"""
  B = self._B;
  l = self._l;
  if type(type(self)) == type(type(other)) and self._l == other._l or \
     isint(other) and -1 <= other>>l <= 0 :
    if l <= B :
      self._x = (self._x-int(other))&((1<<l)-1);
    else :
      _fill(self,(int(self)-int(other))&((1<<l)-1));
  else :
    return NotImplemented;
  return self;

def __sub__(self,other) :
  """Return self minus other, discarding carry"""
  return __isub__(type(self)(self),other);

def __rsub__(self,other) :
  """Return other minus self, discarding carry"""
  l = self._l;
  if isint(other) and -1 <= other>>l <= 0 :
    return type(self)((other-int(self))&((1<<l)-1), l);
  return NotImplemented;


def __getitem__(self,key) :
  """Return bitstring gotten by concatenating the indexed portion(s) of self"""
  if not isinstance(key,tuple) :
    key = (key,);
  B = self._B;
  l = self._l;
  z = l%B;
  x = 0;
  n = 0;
  for k in key :
    if isint(k) :
      if -l <= k < l :
        k %= l;
        if l <= B :
          x = (x<<1) | ((self._x>>(l-1-k))&1);
        else :
          o,r = divmod(k,B);
          y = self._x[o];
          x = (x<<1) | ((y>>(B-1-r))&1);
        n += 1;
      else :
        raise IndexError('bitstring index out of range');
    elif isinstance(k,slice) :
      s = k.indices(l);
      if s[2] == 1 :    # optimization for step==1
        ls = s[1]-s[0];
        if ls :
          x <<= ls;
          n += ls;
          m = (1<<ls)-1;
          if l <= B :
            x |= (self._x>>(l-s[1]))&m;
          else :
            eb,er = divmod(s[1]-1,B);    # last bit
            sb,sr = divmod(s[0],B);      # first bit
            if sb == eb :   # starts and ends in same block
              x |= (self._x[eb]>>(B-1-er))&m;
            else :    # start and end in different blocks
              x |= (self._x[sb]<<(ls+sr-B))&m;
              x |= self._x[eb]>>(B-1-er);
              for i in xrange(sb+1,eb) :
                x |= self._x[i]<<((eb-1-i)*B+1+er);
      else :
        for k in xrange(*s) :
          if l <= B :
            x = (x<<1) | ((self._x>>(l-1-k))&1);
          else :
            o,r = divmod(k,B);
            y = self._x[o];
            x = (x<<1) | ((y>>(B-1-r))&1);
          n += 1;
    else :
      raise TypeError('bitstring index not int or slice');
  return type(self)(x,n);

def __setitem__(self,key,value) :    # this makes bitstring mutable!
  """Set the specified portion(s) of key from successive bits of value"""
  B = self._B;
  l = self._l;
  if not isinstance(key,tuple) :
    key = (key,);
  n = 0;
  for k in key :
    if isint(k) :
      if -l <= k < l :
        n += 1;
      else :
        raise IndexError('bitstring index out of range');
    elif isinstance(k,slice) :
      start,stop,step = k.indices(l);
      n += max(0,(stop-start+step-(1 if step>0 else -1)))//step;
    else :
      raise TypeError('bitstring index not int or slice');
  if type(type(value)) == bitstrings :
    if value._l != n :
      raise TypeError('value wrong size');
    value = int(value);
  elif isint(value) :
    if value >= 1<<n :
      raise TypeError('value too big');
  else :
    raise TypeError('value not bitstring or int');
  for k in key :
    if isint(k) :
      n -= 1;
      k %= l;
      if l <= B :
        if value&(1<<n) :
          self._x |= 1<<(l-1-k);
        else :
          self._x &= ~(1<<(l-1-k));
      else :
        o,r = divmod(k,B);
        if value&(1<<n) :
          self._x[o] |= 1<<(B-1-r);
        else :
          self._x[o] &= ~(1<<(B-1-r));
    elif isinstance(k,slice) :
      s = k.indices(l);
      if s[2] == 1 and B > 1 and s[1]-s[0] > 1:    # optimize for step==1
        ls = s[1]-s[0];
        m = (1<<ls)-1;
        v = (value>>(n-ls))&m;
        if l <= B :
          self._x = self._x&~(m<<(l-s[1])) | (v<<(l-s[1]));
        else :
          sb,sr = divmod(s[0],B);
          eb,er = divmod(s[1]-1,B);
          er += 1;
          if sb == eb :
            self._x[sb] = self._x[sb]&~(m<<(B-er)) | (v<<(B-er));
          else :
            self._x[sb] = self._x[sb]&(-1<<(B-sr))|(v>>(ls-B+sr));
            m = (1<<B)-1;
            for i in xrange(sb+1,eb) :
              self._x[i] = (v>>(B*(eb-1-i)+er))&m;
            self._x[eb] = self._x[eb]&((1<<(B-er))-1)|((v<<(B-er))&m);
        n -= ls;
      else :
        for k in xrange(*s) :
          n -= 1;
          if l <= B :
            if value&(1<<n) :
              self._x |= 1<<(l-1-k);
            else :
              self._x &= ~(1<<(l-1-k));
          else :
            o,r = divmod(k,B);
            if value&(1<<n) :
              self._x[o] |= 1<<(B-1-r);
            else :
              self._x[o] &= ~(1<<(B-1-r));

def __iconcat__(self,*others) :
  """concat bits or bitstrings to self"""
  if self in others :
    c = type(self)(self);    # copy
    others = tuple(o if o != self else c for o in others);
  B = self._B;
  if B<inf:  m = (1<<B)-1;
  x = self._x;
  l = self._l;
  for other in others :
    if isint(other) and 0 <= other <= 1 :
      if l <= B :
        if l < B :
          self._x = x = (x<<1)|other;
        else :
          self._x = x = [x,other<<(B-1)]
      else :
        lr = l%B
        if lr :
          if other : x[-1] |= 1<<(B-1-lr);
        else :
          x.append(other<<(B-1));
      self._l = l = l+1;
      continue;
    elif isinstance(type(other),bitstrings) :
      oB = other._B;
      ol = other._l;
      nl = l+ol;
      if l <= B :
        if nl <= B :
          self._x = x = (x<<ol)+int(other);
          self._l = l = nl;
          continue;
        elif ol <= oB :
          y = (x<<ol)|other._x;
          self._l = l = nl;
          self._x = x = [0]*((l+B-1)//B);
          _filll(self,y);
          continue;
        else :
          self._x = [x<<(B-l)]+[0]*((nl-1)//B);
          self._l = nl;
          _fillr(self,l,other);
          l = nl;
          continue;
      self._x += [0]*((nl-1)//B-(l-1)//B);
      self._l = nl;
      if ol <= oB :
        _filll(self,other._x);
      else :
        _fillr(self,l,other);
      l = nl;
    else :        
      raise TypeError('can only concatenate bits and bitstrings');
  return self;

def __concat__(self,*others) :
  """Return a new bitstring formed by concatenating the args, each a bit or a bitstring"""
  return __iconcat__(type(self)(self),*others);

def __itacnoc__(self,*others) :
  """Concatenate others to self on the left"""
  x = int(self);
  l = self._l;
  for other in others :
    if isint(other) and 0 <= other <= 1 :
      x |= other<<l;
      l += 1;
    elif isinstance(type(other),bitstrings) :
      x |= int(other)<<l;
      l += other._l;
    else :
      raise TypeError('not bitstring');
  B = self._B;
  self._l = l;
  if l <= B :
    self._x = x;
  else :
    self._x = [0]*((l+B-1)//B);
    _fill(self,x,False);
  return self;
  
def __tacnoc__(self,*others) :    # concatenate backwards
  """Return a new bitstring formed by concatening the args in reverse order"""
  x = int(self);
  l = self._l;
  for other in others :
    if isint(other) and 0 <= other <= 1 :
      x |= other<<l;
      l += 1;
    elif isinstance(type(other),bitstrings) :
      x |= int(other)<<l;
      l += other._l;
    else :
      raise TypeError('not bitstring');
  return type(self)(x,l);

def __itrunc__(self,l) :
  """Truncate self to length l"""
  if not isint(l) or l < 0 :
    raise IndexError('length not nonnegative integer');
  B = self._B;
  if l > self._l :    # extend with zeroes
    if l <= B :
      self._x <<= l-self._l;
    else :
      if self._l <= B :
        self._x = [self._x<<(B-self._l)] if self._l else [];
      self._x += [0]*((l+B-1)//B-(self._l+B-1)//B);
  else :    # truncate
    x = self._x;
    if l <= B :
      self._x = x[0]>>(B-l) if self._l > B else x>>(self._l-l);
    else :
      del x[(l+B-1)//B:];
      if l%B : x[-1] &= -1<<(B-l%B);
  self._l = l;
  return self;

def __trunc__(self,l) :
  """Return a bitstring formed by truncating self to length l"""
  if not isint(l) or l < 0 :
    raise IndexError('length not nonnegative integer');
  if l > self._l :    # extend with zeroes
    return __itrunc__(type(self)(self),l);
  B = self._B;
  x = self._x;
  r = type(self)();
  if l <= B:
    r._x = x[0]>>(B-l) if self._l > B else x>>(self._l-l);
  else :
    r._x = x[:(l+B-1)//B];
    if l%B : r._x[-1] &= -1<<(B-l%B);
  r._l = l;
  return r;

def __imul__(self,n) :
  """Concatenate the bitstring to itself |n| times, bitreversed if n < 0"""
  if not isint(n) :
    raise TypeError("Can't multiply bitstring by non int");
  if n <= 0 :
    if n :
      n = -n;
      l = self._l;
      for i in xrange(l//2) :
        self[i],self[l-1-i] = self[l-1-i],self[i];
    else :
      self._x = 0;
      self._l = 0;
  if n > 1 :
    y = type(self)(self);
    for _ in xrange(n-1) :
      self.iconcat(y);
  return self;

def __mul__(self,n) :
  """Return a bitstring comprising |n| copies of self, bitreversed if n < 0"""
  return __imul__(type(self)(self),n);

_bitstring = {};  # chunk -> bitstring

class bitstrings(type) :
  """Class to create bitstring types"""

  def __new__(cls,chunk=inf) :
    try :
      return _bitstring(chunk);
    except :
      pass;
    if not isint(chunk) and chunk != inf :
      raise TypeError('chunk must be infinite or an integer');
    if chunk<=0 :
      raise ValueError('chunk must be positive');
    d = dict(_B=chunk,
             __init__=__init__,
             __repr__=__repr__,
             __str__=__str__,
             __eq__=__eq__,
             __ne__=__ne__,
             __lt__=__lt__,
             __le__=__le__,
             __gt__=__gt__,
             __ge__=__ge__,
             __bool__ = __bool__,
             __nonzero__=__nonzero__,
             __int__=__int__,    # convert to single integer
             __len__=__len__,    # number of bits
             __invert__=__invert__,
             __neg__=__neg__,
             __pos__=__pos__,
             __getitem__=__getitem__,
             __setitem__=__setitem__,
             __imul__=__imul__,      # repeat (int other), or concat (bitstring other)
             __mul__=__mul__,
#             __imod__=__imod__,      # truncate (other is length of result)
#             __mod__=__mod__,
#             __ifloordiv__=__ifloordiv__,    # truncate (other is # bits removed!)
#             __floordiv__=__floordiv__,
#             __divmod__ = __divmod__,    # split, other is # bits in mod)
             __ilshift__=__ilshift__,    # rotate left
             __irshift__=__irshift__,    # roate right
             __lshift__=__lshift__,
             __rshift__=__rshift__,
             __ixor__=__ixor__,
             __xor__=__xor__,
             __rxor__=__xor__,
             __ior__=__ior__,
             __or__=__or__,
             __ror__=__or__,
             __iand__=__iand__,
             __and__=__and__,
             __rand__=__and__,
             __iadd__=__iadd__,
             __add__=__add__,
             __radd__=__add__,
             __isub__=__isub__,
             __sub__=__sub__,
             __rsub__=__rsub__,
             iconcat=__iconcat__,
             concat=__concat__,
             itacnoc=__itacnoc__,
             tacnoc=__tacnoc__,
             itrunc=__itrunc__,
             trunc=__trunc__,
             copy=__copy__,
           );
    name = 'bitstring%d'%(chunk) if chunk < inf else 'bitstring';
    _bitstring[chunk] = b = type.__new__(cls,name,(),d);
    return b;

  def __init__(self,*args,**kwargs) :
    return;

  def __hash__(self) :
    return hash(self.__name__);

  def __eq__(self,other) :
    return self is other;

  def __ne__(self,other) :
    return not self is other;

     
bitstring = bitstrings();
bitstrings(8);
