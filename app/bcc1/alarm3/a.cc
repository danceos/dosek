#include "os.h"
#include "test/test.h"
#include "alarm3_common.h"

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
	TerminateTask();
}

#ifndef FAIL
const unsigned long long max_count = 200000000;
#else
const unsigned long long max_count = 1;
#endif
volatile bool stop = false;

TASK(H3) {
	if (stop == false)
		test_trace('3');
	stop = true;
	TerminateTask();
}

TASK(H4) {
	test_trace('4');
	TerminateTask();
}

TASK(H5) {
	test_trace('5');
    test_trace('[');
    WAIT_FOR_IRQ();
	test_trace(']');

    DisableAllInterrupts();
	test_trace('{');
	WAIT_FOR_IRQ();
	test_trace('}');
    EnableAllInterrupts();
	WAIT_FOR_IRQ();
	test_trace('x');
	TerminateTask();
}


void PreIdleHook() {
	/* The testcase has finished, check the output */
    test_trace_assert("5[3]{}3x");
    test_finish();
    ShutdownMachine();
}
