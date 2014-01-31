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
	ActivateTask(Handler12);
	if (a > 100) {
		ActivateTask(Handler13);
		TerminateTask();
	} else {
		TerminateTask();
	}
}

TASK(Handler12) {
	TerminateTask();
}

TASK(Handler13) {
	TerminateTask();
}
