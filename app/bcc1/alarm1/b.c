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
	ActivateTask(H1);
	TerminateTask();
}

TASK(H3) {
	TerminateTask();
}

