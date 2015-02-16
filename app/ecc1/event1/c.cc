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


TEST_MAKE_OS_MAIN( StartOS(0) );

TASK(H1) {
	test_trace('1');
	SetEvent(H3, E1);
	test_trace('[');
	ActivateTask(H3);
	test_trace(':');
	SetEvent(H3, E1);
	test_trace(']');
	TerminateTask();
}

TASK(H2) {
	TerminateTask();
}

TASK(H3) {
	test_trace('{');
	WaitEvent(E1);
	test_trace('}');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("1[{:}]");
	test_finish();
}
