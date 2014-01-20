#include "os.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareAlarm(A1);
DeclareCounter(C1);


TASK(H1) {
	TerminateTask();
}

TASK(H2) {
	TerminateTask();
}

TASK(H3) {
	TerminateTask();
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


