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
	ChainTask(H1);
}

TASK(H3) {
	ChainTask(H2);
}

ISR(ISR1) {
	ActivateTask(H3);
}

void os_main() {
	OSEKOS_TASK_H1();
}

StatusType OSEKOS_TerminateTask() {
	return E_OK;
	for(;;){};
}

StatusType OSEKOS_ActivateTask(TaskType t) {
	return E_OK;
}


