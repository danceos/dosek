#include "os.h"
#include "alarm3_common.h"
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
	TerminateTask();
}

volatile bool stop;

#ifndef FAIL
const unsigned long long max_count = 200000000;
#else
const unsigned long long max_count = 1;
#endif

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

extern "C" void bar() {
    SuspendAllInterrupts();
	test_trace('<');
	WAIT_FOR_IRQ();
    test_trace('>');
    ResumeAllInterrupts();
}

TASK(H5) {
	test_trace('5');

    SuspendAllInterrupts();
	test_trace('{');

    bar();
    bar();
    bar();

    test_trace('}');
    ResumeAllInterrupts();

    WAIT_FOR_IRQ();
	test_trace('x');
	TerminateTask();
}


void PreIdleHook() {
	/* The testcase has finished, check the output */
    test_trace_assert("5{<><><>}3x");
    test_finish();
    ShutdownMachine();
}
