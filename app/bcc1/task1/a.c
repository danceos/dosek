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

void os_main(void) {
	StartOS();
}

TASK(Handler11) {
	Trace('a');
	ActivateTask(Handler12);
	Trace('b');
	ActivateTask(Handler13);
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
	TraceAssert("ab3c2");
	ShutdownMachine();
}
