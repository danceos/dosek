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

int a;

void test(void) {
	test_start();
	StartOS(0);
}

TASK(Handler11) {
	a++;
	if (a > 3) {
		Trace('T');
		TerminateTask();
	}
	Trace('1');
	ChainTask(Handler13);
}

TASK(Handler12) {
	Trace('2');
	ChainTask(Handler11);
}

TASK(Handler13) {
	Trace('3');
	ActivateTask(Handler12);
	Trace('4');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_start_check();
	TraceAssert((char *)"134213421342T");
	ShutdownMachine();
}


