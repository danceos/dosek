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

int a = 0;

TASK(Handler11) {
	Trace('a');

	while (a < 3) {
		a++;
		Trace('0' + a);
		ActivateTask(Handler13);
		Trace('L');
	}
	Trace('T');
	TerminateTask();
}

TASK(Handler12) {
	Trace('B');
	TerminateTask();
}

TASK(Handler13) {
	Trace('C');
	ActivateTask(Handler12);
	Trace('D');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_start_check();
	TraceAssert((char *)"a1CDL2CDL3CDLTB");
	ShutdownMachine();
}


