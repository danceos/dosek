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

extern "C" void bar() {
	ActivateTask(Handler12);
}

extern "C" void foo() {
	a++;
	return;
}




TASK(Handler11) {
	a++;
	if (a == 100) {
		test_trace('a');
		bar();
		test_trace('b');
		a++;
	} else {
		test_trace('c');
		ActivateTask(Handler12);
		test_trace('d');
		foo();
	}
	test_trace('f');
	ChainTask(Handler13);
}

TASK(Handler12) {
	test_trace('2');
	TerminateTask();
}

TASK(Handler13) {
	test_trace('3');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("cdf32");
	test_finish();
	ShutdownMachine();
}

