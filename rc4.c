/* RC4 description:
   initialize the state array s to the identity permutation, then
   for i from 0 thru 255 and cycling thru the octets of the key in order:
    swap the ith element with the kth element, where
     k has been incremented by the current key octet and by the ith element
   set x and y to 0 (these are updated and used as indices in rc4step)
   rc4step: increment x, then increase y by the xth element,
     then swap the xth and yth elements and use their sum as the index of
     the element returned
   NOTE: all indices are mod 256
*/

#include <stdint.h>

static uint8_t s[256], x, y;    // 258 octets of state information

void rc4init (    // initialize for encryption / decryption
  uint8_t *key,
  uint16_t length
) {
  uint8_t t, i = 0, j = 0, k = 0;
  do s[i]=i; while (++i);
  do t = s[i], s[i] = s[k += key[i%length] + t], s[k] = t; while (++i);
  x = y = 0;
}

uint8_t rc4step () {    // return next pseudo-random octet
  uint8_t t;
  t = s[y += s[++x]], s[y] = s[x], s[x] = t;
  return (s[t += s[y]]);
}

uint8_t rc4back () {    // step back, return last pseudo-random octet
  uint8_t t, u, v, w;
  t = s[x], u = s[y], w = s[v = t + u];
  s[x--] = u, s[y] = t, y -= u;
  return w;
}
