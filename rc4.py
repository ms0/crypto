import sys
if sys.version_info[0] < 3 :
  lmap = map;
else :
  xrange = range;
  lmap = lambda *x: list(map(*x))
  

def rc4(key) :
  """Given an ASCII string or vector of bytes, generate RC4 bytes"""
  l = len(key);
  if not 0 < l <= 256 :
    raise ValueError('key must have at least 1 and at most 256 elements');
  if isinstance(key,str) :
    key = lmap(ord,key);
  for x in key :
    if not (isinstance(x,int) and 0 <= x < 256) :
      raise ValueError('key elements must all be integers in [0,255]')
  state = list(xrange(256));
  j = k = 0;
  for i in xrange(256) :
    t = state[i];
    k = (k+t+key[j])&0xff;
    state[i] = state[k];
    state[k] = t;
    j = (j+1)%l;
  x = 0;
  y = 0;
  while True :
    x = (x+1)&0xff;
    y = (y+state[x])&0xff;
    state[x],state[y] = state[y],state[x];
    yield state[(state[x]+state[y])&0xff]
