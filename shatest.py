from sha2 import *
from sha3 import *

tests = ['',
         'abc', 
         'abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq',
         'abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu',
#         'a'*int(1e6),
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

if __name__ == '__main__' :
  for t in tests :
    print("'%s'"%(t) if len(t) <= 128 else '%s...%s'%(t[:64],t[-64:]));
    for md in mds :
      test(md,t);
