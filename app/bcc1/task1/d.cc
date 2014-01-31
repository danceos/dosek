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
#include "../trace.h"

DeclareTask(Handler11);
DeclareTask(Handler12);
DeclareTask(Handler13);

int a = 11;

extern "C" void bar() {
	Trace('b');
	ActivateTask(Handler13);
}

extern "C" void foo() {
	Trace('f');
	a++;
	return;
}

void test(void) {
	test_start();
	StartOS(0);
}


TASK(Handler11) {
	Trace('1');
	a++;
	if (a == 12) {
		Trace('2');
		ActivateTask(Handler12);
	}

	if (a == 100) {
		Trace('3');
		bar();
		Trace('4');
		a++;
	} else {
		foo();
		Trace('5');
		ActivateTask(Handler13);
	}
	Trace('6');
	TerminateTask();
}

TASK(Handler12) {
	Trace('X');
	TerminateTask();
}

TASK(Handler13) {
	Trace('Y');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_start_check();
	TraceAssert((char *)"12f5Y6X");
	ShutdownMachine();
}


