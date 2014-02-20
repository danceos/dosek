#include "os.h"
#include "test/test.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareTask(H4);

DeclareResource(RES_SCHEDULER);

TEST_MAKE_OS_MAIN(StartOS(0))

extern "C" void bar(void) {
	test_trace('b');
	ActivateTask(H2);
	test_trace('B');
}

bool first_run = true;
TASK(H1) {
	test_trace('1');
	if (first_run) {
		first_run = false;
		test_trace('<');
		ActivateTask(H3);
		bar();
		test_trace('>');
		TerminateTask();
	} else {
		bar();
		TerminateTask();
	}
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

TASK(H5) {
	test_trace('5');
	ActivateTask(H1);
	test_trace('|');
	ChainTask(H1);
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("51<bB>23|1bB2");
	test_finish();
	ShutdownMachine();
}

