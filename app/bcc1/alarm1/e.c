#include "os.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareAlarm(A1);
DeclareCounter(C1);

int a;

TASK(H1) {
	TerminateTask();
}

TASK(H2) {
	if (a>100) {
		ActivateTask(H3);
	}
	TerminateTask();
}

TASK(H3) {
	a++;
	while (a > 3) {
		a++;
		ActivateTask(H1);
	}
	a++;
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


