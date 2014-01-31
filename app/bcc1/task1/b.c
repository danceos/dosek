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
#include "../trace.c"

DeclareTask(Handler11);
DeclareTask(Handler12);
DeclareTask(Handler13);

int a;

void bar() {
	ActivateTask(Handler12);
}

void foo() {
	a++;
	return;
}




TASK(Handler11) {
	a++;
	if (a == 100) {
		Trace('a');
		bar();
		Trace('b');
		a++;
	} else {
		Trace('c');
		ActivateTask(Handler12);
		Trace('d');
		foo();
	}
	Trace('f');
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
	TraceAssert("cdf32");
	ShutdownOS(E_OK);
}


