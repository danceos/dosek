#include "os.h"
#include "test/test.h"
#include "../trace.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareAlarm(A1);
DeclareCounter(C1);

volatile int a;

void test(void) {
	test_start();
	StartOS(0);
}

TASK(H1) {
	Trace('1');
	TerminateTask();
}

TASK(H2) {
	a++;
	Trace('0' + a);
	ActivateTask(H3);
	TerminateTask();
}

TASK(H3) {
	Trace('.');
	while (a <= 3) {};
	Trace(':');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	static int cycle_count;
	cycle_count++;

	if (cycle_count > 5) {
		test_start_check();
		TraceAssert((char *)"1.234:5.:6.:7.:8.:");
		ShutdownMachine();
	}
}
