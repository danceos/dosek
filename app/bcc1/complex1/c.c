/**
 * @defgroup apps Applications
 * @brief The applications...
 */

/**
 * @file
 * @ingroup apps
 * @brief Just a simple test application
 */
#include "os.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);

int a;

TASK(H1) {
	TerminateTask();
}

TASK(H2) {
	TerminateTask();
}

TASK(H3) {
	ChainTask(H1);
}

ISR(ISR1) {
	ActivateTask(H3);
}

