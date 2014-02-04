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

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);

TEST_MAKE_OS_MAIN( StartOS(0))

TASK(H1) {
	test_trace('1');
	TerminateTask();
}

TASK(H2) {
	test_trace('a');
	ActivateTask(H3);
	test_trace('b');
	TerminateTask();
}

TASK(H3) {
	test_trace('3');
	TerminateTask();
}

ISR2(ISR1) {
	test_trace('.');
	ActivateTask(H2);
	test_trace(':');
}


// new syscall to trigger interrupt using local APIC
// for now, any function can be called using syscall(),
// so it is easy to add this for this test.
noinline void __OS_trigger_syscall(uint8_t irq) {
	Machine::trigger_interrupt(irq);
}


PreIdleHook() {
	/* The testcase has finished, check the output */
	static int cycle_count;
	cycle_count++;

	if (cycle_count > 3) {
		test_start_check();
		test_trace_assert((char *)".:ab3.:ab3.:ab3");
		ShutdownMachine();
	} else {
		arch::syscall(__OS_trigger_syscall, 37, true);
	}
}

