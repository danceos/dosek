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

void test(void) {
	test_start();
	StartOS(0);
}


int a;

extern "C" void bar() {
	Trace('b');
	ActivateTask(Handler12);
}

extern "C" void foo() {
	Trace('f');
	a++;
	return;
}




TASK(Handler11) {
	Trace('1');
	a++;
	if (a == 100) {
		bar();
		a++;
	} else {
		foo();
	}
	Trace('X');
	ChainTask(Handler13);
}

TASK(Handler12) {
	Trace('2');
	TerminateTask();
}

TASK(Handler13) {
	Trace('3');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_start_check();
	TraceAssert((char *)"1fX3");
	ShutdownMachine();
}
