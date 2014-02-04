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

TEST_MAKE_OS_MAIN( StartOS(0) )

volatile int a;

TASK(H1) {
	test_trace('1');
	TerminateTask();
}

TASK(H2) {
	test_trace('{');
	ActivateTask(H3);
	test_trace('*');
	ActivateTask(H1);
	test_trace('}');
	TerminateTask();
}

TASK(H3) {
	test_trace('3');
	TerminateTask();
}

ISR2(ISR1) {
	test_trace('.');
	if (a < 1000) {
		test_trace(':');
		ActivateTask(H2);
	}
	a++;
	test_trace('T');
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	static int cycle_count;
	cycle_count++;

	if (cycle_count > 3) {
		test_trace_assert(".:T{*1}3.:T{*1}3.:T{*1}3");
		test_finish();
		ShutdownMachine();
	} else {
		Machine::trigger_interrupt_from_user(37);
	}
}

