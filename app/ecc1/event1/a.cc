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

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareEvent(E1);

TEST_MAKE_OS_MAIN( StartOS(0) );

TASK(H1) {
    ActivateTask(H2);
	WaitEvent(E1);
	TerminateTask();
}

TASK(H2) {
	SetEvent(H1, E1);
	TerminateTask();
}

TASK(H3) {
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("ab3c2");
	test_finish();
	ShutdownMachine();
}
