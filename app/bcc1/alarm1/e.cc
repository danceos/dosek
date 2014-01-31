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
