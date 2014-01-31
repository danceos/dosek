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

extern "C" void bar() {
	Trace('b');
	ActivateTask(Handler13);
}

TASK(Handler11) {
	a++;
	if (a > 3) {
		Trace('1');
		bar();
	}
	Trace('C');
	ChainTask(Handler13);
}

TASK(Handler12) {
	Trace('2');
	ChainTask(Handler11);
}

TASK(Handler13) {
	Trace('3');
	if (a < 5)
		ActivateTask(Handler12);
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_start_check();
	TraceAssert((char *)"C32C32C321b3C321b3C3");
	ShutdownMachine();
}
