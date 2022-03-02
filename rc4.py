from conversions import xrange, lmap

class rc4(object) :

  def __init__(self, key) :
    """Initialize RC4 generator with key"""
    l = len(key);
    if not 0 < l <= 256 :
      raise ValueError('key must have at least 1 and at most 256 elements');
    if isinstance(key,str) :
      key = lmap(ord,key);
    for x in key :
      if not (isinstance(x,int) and 0 <= x < 256) :
        raise ValueError('key elements must all be integers in [0,255]');
    state = list(xrange(256));
    j = k = 0;
    for i in xrange(256) :
      t = state[i];
      k = (k+t+key[j])&0xff;
      state[i] = state[k];
      state[k] = t;
      j = (j+1)%l;
    self._state = state;
    self._x = self._y = 0;

  def __iter__(self) :
    """Return RC4 interator"""
    return self;

  def __next__(self) :
    """Return next octet in RC4 stream"""
    self._x = (self._x + 1) & 0xff;
    self._y = (self._y + self._state[self._x]) & 0xff;
    self._state[self._x], self._state[self._y] = \
      self._state[self._y], self._state[self._x];
    return self._state[(self._state[self._x] + self._state[self._y]) & 0xff]
    
  def __prev__(self) :
    """Return previous octet in RC4 stream"""
    t = self._state[self._x];
    u = self._state[self._y];
    v = self._state[(t + u) & 0xff];
    self._state[self._x] = u;
    self._state[self._y] = t;
    self._x = (self._x - 1) & 0xff;
    self._y = (self._y - u) & 0xff;
    return v;

  next = __next__
  prev = __prev__
