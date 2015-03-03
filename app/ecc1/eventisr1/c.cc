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


DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareEvent(E1);
DeclareEvent(E2);


TEST_MAKE_OS_MAIN( StartOS(0) );

/* This 
 */

TASK(H1) {
	ActivateTask(H2);
	test_trace('1'); 
	WaitEvent(E2);
	test_trace('}');

	/* The testcase has finished, check the output */
	test_trace_assert("1-!}");
	test_finish();
	ShutdownMachine();

	TerminateTask();
}

TASK(H2) {
	test_trace('-');
	// Trigger ISR2
	Machine::trigger_interrupt_from_user(37);
	TerminateTask();
}

TASK(H3) {
	TerminateTask();
}

ISR2(ISR1) {
	test_trace('!');
	SetEvent(H1, E2);
}

void PreIdleHook() {
}
