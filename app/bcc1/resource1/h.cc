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

int path_selector = 0;

TASK(H1) {
	test_trace('1');
	ChainTask(H2);
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
	if (path_selector == 0) {
		test_trace('{');
		ActivateTask(H1);
		test_trace('}');
	} else {
		test_trace('[');
		GetResource(R234);
		test_trace('(');
		ActivateTask(H1);
		test_trace(')');
		ReleaseResource(R234);
		test_trace(']');
	}
	test_trace('*');
	TerminateTask();
}

TASK(H5) {
	test_trace('5');
	ActivateTask(H4);
	test_trace('|');
	path_selector = 1;
	ChainTask(H4);
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("54{12}*|4[(1)2]*");
	test_finish();
	ShutdownMachine();
}

