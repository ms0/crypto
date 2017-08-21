from sha2 import *
from sha3 import *

tests = ['',
         'abc', 
         'abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq',
         'abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu',
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

for t in tests :
  print("'%s'"%(t));
  for md in mds :
    print('%s: %s'%(md,globals()[md](bitstring(t))));
