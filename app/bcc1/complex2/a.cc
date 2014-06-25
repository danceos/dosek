/**
 * @defgroup apps Applications
 * @brief The applications...
 */

/**
 * @file
 * @ingroup apps
 * @brief Just a simple test application
 */
#include "os.h"
#include "test/test.h"
#include "syscall.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);

TEST_MAKE_OS_MAIN(StartOS(0))

static int cycle_count;

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
	Machine::trigger_interrupt_from_user(37);
	test_trace('-');
	TerminateTask();
}

TASK(H4) {
	test_trace('4');
	TerminateTask();
}

TASK(H5) {
	test_trace('5');
	ActivateTask(H3);
	Machine::nop();
	TerminateTask();
}

ISR2(ISR1) {
	test_trace('.');
	ActivateTask(H1);
	test_trace(':');
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("53.:-1");
	test_finish();
	ShutdownMachine();
}

