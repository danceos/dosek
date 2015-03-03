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

int a = 0;

extern "C" void bar() {
	test_trace('b');
	ActivateTask(Handler13);
}

TASK(Handler11) {
	a++;
	if (a > 3) {
		test_trace('1');
		bar();
	}
	test_trace('C');
	ChainTask(Handler13);
}

TASK(Handler12) {
	test_trace('2');
	ChainTask(Handler11);
}

TASK(Handler13) {
	test_trace('3');
	if (a < 5)
		ActivateTask(Handler12);
	Machine::nop();
	TerminateTask();
}

void PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("C32C32C321b3C321b3C3");
	test_finish();
	ShutdownMachine();
}
