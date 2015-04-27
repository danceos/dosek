#include "os.h"
#include "test/test.h"
#include "machine.h"

DeclareTask(Coord); // Non-Preemptable
DeclareTask(BT1);   // Prio: 3
DeclareTask(BT2);   // Prio: 11
DeclareTask(ET1);   // Prio: 2
DeclareTask(ET2);   // Prio: 10
DeclareEvent(E1);

TEST_MAKE_OS_MAIN( StartOS(0) );

TASK(Coord) {
	test_trace('C');
	ActivateTask(ET1);
	test_trace('>');
	TerminateTask();
}

TASK(BT1) {
	test_trace('1');
	static void *stackptr = 0;
	int dummy;
	if (stackptr == 0 || &dummy == stackptr) {
		test_trace('C');
		stackptr = &dummy;
	}
	TerminateTask();
}

TASK(BT2) {
	test_trace('2');
	ChainTask(ET2); // switch to shared stack
}

TASK(ET1) {
	test_trace(':');
	ActivateTask(BT1);
	ActivateTask(BT1);
	ChainTask(BT1);
}

TASK(ET2) {
	test_trace('?');
	WaitEvent(E1);
	test_trace('!');
	TerminateTask();
}

void PreIdleHook() {
	/* The testcase has finished, check the output */
	test_trace_assert("C>:1C1C1C");
	test_finish();
	ShutdownMachine();
}
