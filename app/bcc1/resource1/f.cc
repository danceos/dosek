#include "os.h"
#include "test/test.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareTask(H4);
DeclareTask(H5);
DeclareResource(RES_SCHEDULER);
DeclareResource(R234);
DeclareResource(R345);


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
	GetResource(R345);
	test_trace('<');

	GetResource(R234);
	test_trace('{');
	ActivateTask(H3);
	Machine::nop();
	ActivateTask(H2);
	Machine::nop();
	ActivateTask(H1);
	test_trace('}');
	ReleaseResource(R234);

	test_trace('>');
	ReleaseResource(R345);

	test_trace('.');
	TerminateTask();
}

TASK(H5) {
	ChainTask(H4);
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("4<{1}2>3.");
	test_finish();
	ShutdownMachine();
}

