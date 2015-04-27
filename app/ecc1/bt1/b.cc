#include "os.h"
#include "test/test.h"
#include "machine.h"

DeclareTask(Coord); // Non-Preemptable
DeclareTask(BT1);   // Prio: 3
DeclareTask(BT2);   // Prio: 11
DeclareTask(ET1);   // Prio: 2
DeclareTask(ET2);   // Prio: 10

TEST_MAKE_OS_MAIN( StartOS(0) );

TASK(Coord) {
	test_trace('C');
	ActivateTask(BT1);
	test_trace('>');
	TerminateTask();
}

TASK(BT1) {
	test_trace('1');
	ActivateTask(ET1);
	test_trace('(');
	ActivateTask(ET2);
	test_trace(')');
	TerminateTask();
}

TASK(BT2) {
	test_trace('2');
	TerminateTask();
}

TASK(ET1) {
	test_trace(':');
	TerminateTask();
}

TASK(ET2) {
	test_trace('!');
	TerminateTask();
}

void PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("C>1(!):");
	test_finish();
	ShutdownMachine();
}
