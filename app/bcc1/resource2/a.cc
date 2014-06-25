#include "os.h"
#include "test/test.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareResource(RES_SCHEDULER);
DeclareResource(R345);

#ifndef FAIL
#define MARK_A 1000000
#define MARK_B 2000000
#else
#define MARK_A 10
#define MARK_B 10
#endif

TEST_MAKE_OS_MAIN(StartOS(0))
volatile int i = 0;

TASK(H1) {
	test_trace('1');
	TerminateTask();
}

TASK(H2) {
	test_trace('2');
	TerminateTask();
}

TASK(H3) {
	if (i == MARK_A) {
		test_trace('3');
		while (i < MARK_B) i++;
	}
	TerminateTask();
}

TASK(H4) {
	test_trace('4');
	TerminateTask();
}

TASK(H5) {
	test_trace('5');
	GetResource(R345);
	test_trace('.');
	while (i < MARK_A) i++;
	test_trace('.');
	ReleaseResource(R345);
	while (i < MARK_B);
	test_trace('*');
	TerminateTask();
}

PreIdleHook() {
	/* The testcase has finished, check the output */
	test_start_check();
	test_trace_assert((char *)"5..3*");
	test_finish();
	ShutdownMachine();
}
