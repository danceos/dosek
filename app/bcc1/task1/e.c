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

void os_main() {
	OSEKOS_TASK_Handler11();
}

StatusType OSEKOS_TerminateTask() {
	return E_OK;
	for(;;){};
}

StatusType OSEKOS_ActivateTask(TaskType t) {
	return E_OK;
}

