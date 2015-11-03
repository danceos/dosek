#ifndef __OSEK_V_SYSCALL
#define __OSEK_V_SYSCALL

#define syscall(sys) do { (sys)(0);} while(0)
#endif
