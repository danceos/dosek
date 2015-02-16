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
#include "machine.h"


DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareEvent(E1);
DeclareEvent(E2);



TEST_MAKE_OS_MAIN( StartOS(0) );

TASK(H1) {
	test_trace('1');
	ActivateTask(H2);
	ActivateTask(H3);

	test_trace('[');
	SetEvent(H3, E1);
	test_trace(']');
	TerminateTask();
}

TASK(H2) {
	test_trace('(');
	SetEvent(H3, E2);
	test_trace(')');
	TerminateTask();
}

TASK(H3) {
	while (1) {
		test_trace('{');
		WaitEvent(E1 | E2);
		test_trace('.');
		ClearEvent(E1 | E2);
		test_trace('}');
	}
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("1{[.}{](.}{)");
	test_finish();
}
