#include "os.h"
#include "test/test.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareAlarm(A1);
DeclareCounter(C1);

TEST_MAKE_OS_MAIN(StartOS(0))

volatile int a;

TASK(H1) {
	test_trace('X');
	TerminateTask();
}

TASK(H2) {
#ifndef FAIL
	a++;
#else
	// Stop immedately
	a = 100;
#endif
	test_trace('0' + a);
	ActivateTask(H3);
	Machine::nop();
	TerminateTask();
}

TASK(H3) {
	test_trace('.');
	while (a <= 3) {};
	test_trace(':');
	TerminateTask();
}

void PreIdleHook() {
	/* The testcase has finished, check the output */
	static int cycle_count;
	cycle_count++;

	if (cycle_count > 5) {
		test_trace_assert("1.234:5.:6.:7.:8.:");
		test_finish();
		ShutdownMachine();
	}
}
