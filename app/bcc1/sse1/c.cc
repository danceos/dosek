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
	ActivateTask(H3);
	test_trace('B');
}

bool first_run = true;
TASK(H1) {
	test_trace('2');
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
	GetResource(RES_SCHEDULER);
	test_trace('{');
	if (first_run) {
		first_run = false;
		ActivateTask(H2);
		bar();
		ReleaseResource(RES_SCHEDULER);
	} else {
		bar();
		ReleaseResource(RES_SCHEDULER);
	}
	test_trace('}');
	TerminateTask();
}

TASK(H5) {
	test_trace('5');
	ActivateTask(H4);
	test_trace('|');
	ChainTask(H4);
}

void PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("54{bB23}|4{bB3}");
	test_finish();
	ShutdownMachine();
}

