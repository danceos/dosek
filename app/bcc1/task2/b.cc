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
#include "syscall.h"


DeclareTask(Handler11);
DeclareTask(Handler12);
DeclareTask(Handler13);

TEST_MAKE_OS_MAIN(StartOS(0))

int a;
TASK(Handler11) {
	test_trace('a');
	ActivateTask(Handler12);
	if (a < 100) {
		test_trace('b');
		ActivateTask(Handler13);
		test_trace('c');
		TerminateTask();
	} else {
		test_trace('d');
		TerminateTask();
	}
}

TASK(Handler12) {
	test_trace('2');
	TerminateTask();
}

TASK(Handler13) {
	test_trace('3');
	TerminateTask();
}

PreIdleHook() {
	test_start_check();
	test_trace_assert((char *)"abc32");
	ShutdownMachine();
}

