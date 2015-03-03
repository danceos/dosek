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
	ChainTask(H3);
}

TASK(H2) {
	test_trace('2');
	ActivateTask(H5);
	Machine::nop();
	ActivateTask(H3);
	Machine::nop();
	TerminateTask();
}

TASK(H3) {
	test_trace('3');
	TerminateTask();
}

TASK(H4) {
	test_trace('5');
	TerminateTask();
}

TASK(H5) {
	test_trace('5');
	GetResource(R345);
	test_trace('{');
	ActivateTask(H2);
	test_trace('}');
	ReleaseResource(R345);
	test_trace('T');
	TerminateTask();
}

void PreIdleHook() {
	/* The testcase has finished, check the output */
	test_start_check();
	test_trace_assert((char *)"5{2}3T");
	test_finish();
	ShutdownMachine();
}

