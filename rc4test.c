#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

void rc4init(uint8_t *key, uint16_t length);
uint8_t rc4step();
uint8_t rc4back();

void printstream(uint8_t *k, uint n) {
  rc4init(k,strlen(k));
  while (n--) printf("%02x",rc4step());
  printf("\n");
}

void printmaerts(uint n) {
  while (n--) printf("%02x",rc4back());
  printf("\n");	
}

char *rs = "This is not some random string? ";    // 32 octets

int main() {
  printstream("Key",40);
  printmaerts(40);
  printstream("Wiki",40);
  printmaerts(40);
  printstream("Secret",40);
  printmaerts(40);
  uint8_t s[256];
  int i;
  for (i=0; i<256; ++i) s[i] = rs[i%32];
  rc4init(s,32);
  uint8_t *a = (uint8_t *)malloc(1<<20);
  for (i=0; i < 1<<20; ++i) a[i] = rc4step();
  while (i--) {
    if (a[i] != rc4back()) {
      printf("failed at index %d",i);
      break;
    }
  }
  rc4init(s,256);
  for (i=0; i < 1<<20; ++i) {
    if (a[i] != rc4step()) {
      printf("failed at index %d",i);
      break;
    }
  }
  free(a);
}
