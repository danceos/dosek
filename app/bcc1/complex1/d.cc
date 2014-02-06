/**
 * @defgroup apps Applications
 * @brief The applications...
 */

/**
 * @file
 * @ingroup apps
 * @brief This testcase checks the function of ALARMCALLBACKS. An
 * interrupt is triggered from an alarmcallback. The ISR2 enabled
 * task H1 which terminated. Since the ISR was activated by an alarm,
 * the Task H2 is executed after H1 (priority!)
 */
#include "os.h"
#include "test/test.h"
#include "syscall.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareAlarm(A1);
DeclareCounter(C1);

TEST_MAKE_OS_MAIN(StartOS(0))

static int cycle_count;

TASK(H1) {
	test_trace('1');
	TerminateTask();
}

TASK(H2) {
	test_trace('2');
	TerminateTask();
}

TASK(H3) {
	test_trace('3');
	TerminateTask();
}

ISR2(ISR1) {
	test_trace('.');
	ActivateTask(H1);
	test_trace(':');
}

ALARMCALLBACK(A1) {
	test_trace('<');
	Machine::trigger_interrupt(37);
	test_trace('>');
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	cycle_count++;

	if (cycle_count > 3) {
		test_start_check();
		test_trace_assert((char *)"<>.:12<>.:12<>.:12");
		ShutdownMachine();
	}
}

