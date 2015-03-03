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

TASK(H1) {
	test_trace('1');
	TerminateTask();
}

TASK(H2) {
	test_trace('2');
	ChainTask(H1);
}

TASK(H3) {
	test_trace('3');
	ChainTask(H2);
}

ISR2(ISR1) {
	test_trace('.');
	test_trace_assert(".");
	test_finish();
	ShutdownMachine();
}


void PreIdleHook() {
	/* The testcase has finished, check the output */
	static int cycle_count;
	cycle_count++;

	if (cycle_count > 3) {
		ShutdownMachine();
	} else {
		Machine::trigger_interrupt_from_user(37);
	}
}

