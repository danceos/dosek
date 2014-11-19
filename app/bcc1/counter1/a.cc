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
#include "machine.h"


// Test memory protection (spanning over more than one 4k page in x86)
//volatile int testme[1024*4*10] __attribute__ ((section (".data.Handler12")));

DeclareTask(Handler11);
DeclareTask(Handler12);
DeclareTask(Handler13);

DeclareAlarm(A1);
DeclareCounter(C1);

TEST_MAKE_OS_MAIN( StartOS(0) )

TASK(Handler11) {
	test_trace('1');
	IncrementCounter(C1);

	test_trace('+');
	IncrementCounter(C1);

	test_trace('+');
	IncrementCounter(C1);

	test_trace('>');
	IncrementCounter(C1);

	test_trace('>');
	IncrementCounter(C1);
	test_trace('>');
	IncrementCounter(C1);


	TickType tick;
	GetAlarm(A1, &tick);
	test_trace(tick + '0');

	TerminateTask();
}

TASK(Handler12) {
	test_trace('2');
	TerminateTask();
}

TASK(Handler13) {
	test_trace('&');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("1++2>>>23");
	test_finish();
	ShutdownMachine();
}
