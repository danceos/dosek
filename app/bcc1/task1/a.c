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

TASK(Handler11) {
	ActivateTask(Handler12);
	ActivateTask(Handler13);
	TerminateTask();
}

TASK(Handler12) {
	TerminateTask();
}

TASK(Handler13) {
	TerminateTask();
}
