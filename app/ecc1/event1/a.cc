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

TEST_MAKE_OS_MAIN( StartOS(0) );

/* This is a system test, that does autostart H1.  H1 does wait for a
   event(1) for the first time. This happens after H2 was
   activated. H2 does set the event for H1, and is preempted by
   H1. The second wait event does not result in a waiting state.
 */

TASK(H1) {
	test_trace('1');
    ActivateTask(H2);
	test_trace('[');
	WaitEvent(E1); /* (1) */
	test_trace(']');
	WaitEvent(E1);
	test_trace('}');
	TerminateTask();
}

TASK(H2) {
	test_trace('&');
	SetEvent(H1, E1);
	test_trace('*');
	TerminateTask();
}

TASK(H3) {
	TerminateTask();
}

void PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("1[&]}*");
	test_finish();
	ShutdownMachine();
}
