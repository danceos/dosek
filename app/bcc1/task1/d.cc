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

int a = 11;

extern "C" void bar() {
	test_trace('b');
	ActivateTask(Handler13);
}

extern "C" void foo() {
	test_trace('f');
	a++;
	return;
}

TASK(Handler11) {
	test_trace('1');
	a++;
	if (a == 12) {
		test_trace('2');
		ActivateTask(Handler12);
	}

	if (a == 100) {
		test_trace('3');
		bar();
		test_trace('4');
		a++;
	} else {
		foo();
		test_trace('5');
		ActivateTask(Handler13);
	}
	test_trace('6');
	TerminateTask();
}

TASK(Handler12) {
	test_trace('X');
	TerminateTask();
}

TASK(Handler13) {
	test_trace('Y');
	TerminateTask();
}

void PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("12f5Y6X");
	test_finish();
	ShutdownMachine();
}


