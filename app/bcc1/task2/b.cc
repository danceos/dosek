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
#include "syscall.h"


DeclareTask(Handler11);
DeclareTask(Handler12);
DeclareTask(Handler13);

void test(void) {
	test_start();
	StartOS(0);
}

int a;
TASK(Handler11) {
	Trace('a');
	ActivateTask(Handler12);
	if (a < 100) {
		Trace('b');
		ActivateTask(Handler13);
		Trace('c');
		TerminateTask();
	} else {
		Trace('d');
		TerminateTask();
	}
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
	test_start_check();
	TraceAssert((char *)"abc32");
	ShutdownMachine();
}

