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

DeclareTask(Handler11);
DeclareTask(Handler12);
DeclareTask(Handler13);

int a;

TASK(Handler11) {
	ChainTask(Handler13);
}

TASK(Handler12) {
	ChainTask(Handler11);
}

TASK(Handler13) {
	ActivateTask(Handler12);
	TerminateTask();
}

