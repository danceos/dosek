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

	while (a < 5) {
		a++;
		ActivateTask(Handler13);
	}

	TerminateTask();
}

TASK(Handler12) {
	TerminateTask();
}

TASK(Handler13) {
	ActivateTask(Handler12);
	TerminateTask();
}

