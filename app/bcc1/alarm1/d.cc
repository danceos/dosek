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
	Trace('a');
	ActivateTask(H3);
	Trace('b');
	TerminateTask();
}

TASK(H2) {
	Trace('2');
	ChainTask(H1);
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
		TraceAssert((char *)"2ab32ab32ab3");
		ShutdownMachine();
	}
}
