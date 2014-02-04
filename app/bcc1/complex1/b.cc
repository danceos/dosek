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

TEST_MAKE_OS_MAIN(StartOS(0))

// new syscall to trigger interrupt using local APIC
// for now, any function can be called using syscall(),
// so it is easy to add this for this test.
noinline void __OS_trigger_syscall(uint8_t irq) {
	Machine::trigger_interrupt(irq);
}

static int cycle_count;

TASK(H1) {
	test_trace('1');
	TerminateTask();
}

TASK(H2) {
	test_trace('2');
    arch::syscall(__OS_trigger_syscall, 37, true);
	test_trace('_');
	TerminateTask();
}

TASK(H3) {
	test_trace('3');
	TerminateTask();
}

ISR2(ISR1) {
	test_trace('{');
	ActivateTask(H3);
	test_trace('}');
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	cycle_count++;

	if (cycle_count > 3) {
		test_start_check();
		test_trace_assert((char *)"2{}_32{}_32{}_3");
		ShutdownMachine();
	}
}

