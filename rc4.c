/* RC4 description:
   initialize the state to the identity permutation, then
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

static uint8_t state[256], x, y;    // 258 octets of state information

void rc4init (    // initialize for encryption / decryption
  uint8_t *key,
  uint16_t length
) {
  uint8_t t, i = 0, j = 0, k = 0;
  do state[i]=i; while (++i);
  do t = state[i], state[i] = state[k += key[j] + t], state[k] = t;
  while (j = (j+1)%length, ++i);
  x = y = 0;
}

uint8_t rc4step () {    // return next pseudo-random octet
  uint8_t t;
  t = state[y += state[++x]], state[y] = state[x], state[x] = t;
  return (state[t += state[y]]);
}

uint8_t rc4back () {    // step back, return last pseudo-random octet
  uint8_t t, u, v, w;
  t = state[x], u = state[y], w = state[v = t + u];
  state[x--] = u, state[y] = t, y -= u;
  return w;
}
