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

int a;

TASK(Handler11) {
	a++;
	if (a > 3) {
		test_trace('T');
		TerminateTask();
	}
	test_trace('1');
	ChainTask(Handler13);
}

TASK(Handler12) {
	test_trace('2');
	ChainTask(Handler11);
}

TASK(Handler13) {
	test_trace('3');
	ActivateTask(Handler12);
	test_trace('4');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("134213421342T");
	test_finish();
	ShutdownMachine();
}


