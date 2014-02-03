#include "os.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareAlarm(A1);
DeclareCounter(C1);

#include "test/test.h"
#include "../trace.h"

void test(void) {
	test_start();
	StartOS(0);
}

int a;

TASK(H1) {
	Trace('1');
	TerminateTask();
}

TASK(H2) {
	Trace('.');
	if (a < 5) {
		Trace('A');
		ActivateTask(H3);
		Trace('a');
	}
	Trace('T');
	TerminateTask();
}

TASK(H3) {
	Trace('3');
	while (a < 3) {
		a++;
		Trace('H');
		ActivateTask(H1);
		Trace('h');
	}
	Trace('t');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	static int cycle_count;
	cycle_count++;

	if (cycle_count > 3) {
		test_start_check();
		TraceAssert((char *)".AaT3H1hH1hH1ht.AaT3t.AaT3t");
		ShutdownMachine();
	}
}
