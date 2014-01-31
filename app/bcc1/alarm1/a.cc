#include "os.h"
#include "test/test.h"
#include "../trace.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareAlarm(A1);
DeclareCounter(C1);

void test(void) {
	test_start();
	StartOS(0);
}

TASK(H1) {
	Trace('1');
	TerminateTask();
}

TASK(H2) {
	Trace('2');
	TerminateTask();
}

TASK(H3) {
	Trace('3');

	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	static int cycle_count;
	cycle_count++;

	if (cycle_count > 3) {
		test_start_check();
		TraceAssert((char *)"222");
		ShutdownMachine();
	}
}
