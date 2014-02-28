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
	test_trace('2');
	/* The testcase has finished, check the output */
    test_trace_assert("32");
    test_finish();
    ShutdownMachine();
	TerminateTask();
}

TASK(H3) {
	test_trace('3');
	ChainTask(H2);
}

TASK(H4) {
	test_trace('4');
	TerminateTask();
}

TASK(H5) {
	test_trace('5');
	TerminateTask();
}
