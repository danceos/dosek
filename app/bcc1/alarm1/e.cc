#include "os.h"
#include "test/test.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareAlarm(A1);
DeclareCounter(C1);

TEST_MAKE_OS_MAIN(StartOS(0))

int a;

TASK(H1) {
	test_trace('1');
	TerminateTask();
}

TASK(H2) {
	test_trace('.');
	if (a < 5) {
		test_trace('A');
		ActivateTask(H3);
		test_trace('a');
	}
	test_trace('T');
	TerminateTask();
}

TASK(H3) {
	test_trace('3');
	while (a < 3) {
		a++;
		test_trace('H');
		ActivateTask(H1);
		test_trace('h');
	}
	test_trace('t');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	static int cycle_count;
	cycle_count++;

	if (cycle_count > 3) {
		test_trace_assert(".AaT3H1hH1hH1ht.AaT3t.AaT3t");
		test_finish();
		ShutdownMachine();
	}
}
