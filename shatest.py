from sha2 import *
from sha3 import *

tests = ['',
         'abc', 
         'abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq',
         'abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu',
         'a'*int(1e6),
#         'abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmno'*(1<<24),
        ]

SHA3_224x = lambda x:b3x(SHA3_224(b3x(x)));
SHA3_256x = lambda x:b3x(SHA3_256(b3x(x)));
SHA3_384x = lambda x:b3x(SHA3_384(b3x(x)));
SHA3_512x = lambda x:b3x(SHA3_512(b3x(x)));

mds = ['SHA1',
       'SHA224',
       'SHA256',
       'SHA384',
       'SHA512',
       'SHA512_224',
       'SHA512_256',
       'SHA3_224x',
       'SHA3_256x',
       'SHA3_384x',
       'SHA3_512x',
      ];

def test(d,m) :    # digest, message
  md = globals()[d];
  print('%s: %s'%(d,md(bitstring(m))));


from timeit import timeit, default_timer

try:
  from timer import process_time
except Exception :
  process_time = default_timer;

from gc import collect

def timing(name,setup,stmt,repeat=1) :
  """Print time taken by stmt"""
  collect();
  t = timeit(
    stmt=stmt,
    setup='from shatest import bitstring,mds,tests,SHA1,SHA224,SHA256,SHA384,SHA512,SHA512_224,SHA512_256,SHA3_224x,SHA3_256x,SHA3_384x,SHA3_512x\n'+setup,
    timer=process_time,number=repeat);
  print('%s\t%.3f ms'%(name,t/repeat*1000));

if __name__ == '__main__' :
  for md in mds :
    timing(md,'','%s(bitstring(""))'%(md));
  for t in tests :
    print("'%s'"%(t) if len(t) <= 128 else '%s...%s'%(t[:64],t[-64:]));
    for md in mds :
      test(md,t);
