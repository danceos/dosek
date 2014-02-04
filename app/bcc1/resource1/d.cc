#include "os.h"
#include "test/test.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareTask(H4);
DeclareTask(H5);
DeclareResource(RES_SCHEDULER);

TEST_MAKE_OS_MAIN(StartOS(0))

TASK(H1) {
	test_trace('1');
	TerminateTask();
}

TASK(H2) {
	test_trace('2');
	TerminateTask();
}

TASK(H3) {
	test_trace('3');
	TerminateTask();
}

TASK(H4) {
	test_trace('4');
	TerminateTask();
}

extern "C" void bar() {
	int counter = 0;
	GetResource(RES_SCHEDULER);
	do {
		test_trace('{');
		// Has higher priority, but it is not scheduled
		ActivateTask(H2);
		test_trace('}');
	} while (++counter < 3);
	ReleaseResource(RES_SCHEDULER);
}

TASK(H5) {
	test_trace('5');
	int counter = 0;
	GetResource(RES_SCHEDULER);
	while (++counter < 3) {
		test_trace('<');
		// Has higher priority, but it is not scheduled
		ActivateTask(H1);
		test_trace('>');
	}
	ReleaseResource(RES_SCHEDULER);
	test_trace('T');
	bar();
	test_trace('X');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("5<><>1T{}{}{}2X");
	test_finish();
	ShutdownMachine();
}

