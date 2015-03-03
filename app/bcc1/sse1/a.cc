#include "os.h"
#include "test/test.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareTask(H4);

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

TASK(H5) {
	test_trace('5');
	ActivateTask(H4);
	test_trace('+');
	ChainTask(H4);
}

void PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("54+4");
	test_finish();
	ShutdownMachine();
}

