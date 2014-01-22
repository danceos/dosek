#ifndef SIGNALINFO_H
#define SIGNALINFO_H

/* signal_functions.h
   Header file for signal_functions.c.
*/

#include <signal.h>

int printSigMask(const char *msg);

int printPendingSigs(const char *msg);

void printSigset(const char *ldr, const sigset_t *mask);

#endif
