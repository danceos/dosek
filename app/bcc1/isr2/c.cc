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
#include "syscall.h"


DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);

void test(void) {
	test_start();
	StartOS(0);
}


volatile int a;

TASK(H1) {
	Trace('1');
	TerminateTask();
}

TASK(H2) {
	Trace('{');
	ActivateTask(H3);
	Trace('*');
	ActivateTask(H1);
	Trace('}');
	TerminateTask();
}

TASK(H3) {
	Trace('3');
	TerminateTask();
}

ISR2(ISR1) {
	Trace('.');
	if (a < 1000) {
		Trace(':');
		ActivateTask(H2);
	}
	a++;
	Trace('T');
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
		TraceAssert((char *)".:T{*1}3.:T{*1}3.:T{*1}3");
		ShutdownMachine();
	} else {
		arch::syscall(__OS_trigger_syscall, 37, true);
	}
}

