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

TASK(Handler11) {
	Trace('a');
	ActivateTask(Handler13);
	Trace('b');
	ActivateTask(Handler12);
	Trace('c');
	TerminateTask();
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
	TraceAssert((char *)"abc32");
	ShutdownMachine();
}
