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
	unsigned int a = 0;

	a++;
	a++;


	ActivateTask(Handler12);

	a++;
	a++;

	ActivateTask(Handler13);

	a++;
	a++;

	TerminateTask();
}

TASK(Handler12) {
	unsigned int a = 0;

	a++;
	a++;
	a++;

	TerminateTask();
}

TASK(Handler13) {
	unsigned int a = 0;

	a++;
	a++;
	a++;
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


