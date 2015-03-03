#include "os.h"
#include "test/test.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareAlarm(A1);
DeclareCounter(C1);

TEST_MAKE_OS_MAIN(StartOS(0))

TASK(H1) {
	test_trace('1');
	TerminateTask();
}

TASK(H2) {
	test_trace('a');
	ActivateTask(H1);
	test_trace('b');
	TerminateTask();
}

TASK(H3) {
	test_trace('3');
	TerminateTask();
}


void PreIdleHook() {
	/* The testcase has finished, check the output */
	static int cycle_count;
	cycle_count++;

	if (cycle_count > 3) {
		test_trace_assert("a1ba1ba1b");
		test_finish();
		ShutdownMachine();
	}
}
