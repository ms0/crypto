/* RC4 description:
   initialize the state array s to the identity permutation, then
   for i from 0 thru 255 and cycling thru the octets of the key in order:
    swap the ith element with the jth element, where
     j has been incremented by the current key octet and by the ith element
   set i and j to 0 (these are updated and used as indices in rc4step)
   rc4step: increment i, then increase j by the ith element,
     then swap the ith and jth elements and use their sum as the index of
     the element returned
   NOTE: all indices are mod 256
*/

#include <stdint.h>

static uint8_t s[256], i, j;    // 258 octets of state information

void rc4init (uint8_t *key, uint16_t length) {    // initialize state
  uint8_t t;
  i = j = 0;
  do s[i]=i; while (++i);
  do t = s[i], s[i] = s[j += key[i%length] + t], s[j] = t; while (++i);
  j = 0;
}

uint8_t rc4step () {    // return next pseudo-random octet
  uint8_t t, u;
  t = s[j += s[++i]], s[j] = u = s[i], s[i] = t;
  return (s[t += u]);
}

uint8_t rc4back () {    // step back, return last pseudo-random octet
  uint8_t t, u, v;
  t = s[i], u = s[j], v = s[v = t + u], s[i--] = u, s[j] = t, j -= u;
  return v;
}
