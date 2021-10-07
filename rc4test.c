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

int main() {
  printstream("Key",40);
  printmaerts(40);
  printstream("Wiki",40);
  printmaerts(40);
  printstream("Secret",40);
  printmaerts(40);
}
