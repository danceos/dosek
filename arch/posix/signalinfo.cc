
#include <string.h>
#include <signal.h>
#include "signalinfo.h"           /* Declares functions defined here */
#include "output.h"

/* NOTE: All of the following functions employ output, which
   is not async-signal-safe As such, these
   functions are also not async-signal-safe (i.e., beware of
   indiscriminately calling them from signal handlers). */

/* Print list of signals within a signal set */
void printSigset(const char *prefix, const sigset_t *sigset) {
    int sig, cnt;
    debug << prefix;
    cnt = 0;
    for (sig = 1; sig < NSIG; sig++) {
        if (sigismember(sigset, sig)) {
            cnt++;
            debug << "X";
        } else {
            debug << "-";
        }
    }

    if (cnt == 0) {
        debug << "<empty signal set>" << endl;
    }
}

/* Print mask of blocked signals for this process */
int printSigMask(const char *msg) {
    sigset_t currMask;

    if (msg != NULL) {
        debug << msg;
    }

    if (sigprocmask(SIG_BLOCK, NULL, &currMask) == -1) {
        return -1;
    }

    printSigset("\t\t", &currMask);
    debug << "\n";

    return 0;
}

/* Print signals currently pending for this process */
int printPendingSigs(const char *msg) {
    sigset_t pendingSigs;

    if (msg != NULL) {
        //fprintf(of, "%s", msg);
        debug << msg;
    }

    if (sigpending(&pendingSigs) == -1) {
        return -1;
    }

    printSigset("\t\t", &pendingSigs);

    return 0;
}


