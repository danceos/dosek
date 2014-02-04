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

DeclareTask(Handler11);
DeclareTask(Handler12);
DeclareTask(Handler13);

TEST_MAKE_OS_MAIN( StartOS(0) )

int a = 0;

TASK(Handler11) {
	test_trace('a');

	while (a < 3) {
		a++;
		test_trace('0' + a);
		ActivateTask(Handler13);
		test_trace('L');
	}
	test_trace('T');
	TerminateTask();
}

TASK(Handler12) {
	test_trace('B');
	TerminateTask();
}

TASK(Handler13) {
	test_trace('C');
	ActivateTask(Handler12);
	test_trace('D');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("a1CDL2CDL3CDLTB");
	test_finish();
	ShutdownMachine();
}


