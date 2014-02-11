#include "os.h"
#include "test/test.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareResource(RES_SCHEDULER);
DeclareResource(R234);
DeclareResource(R345);


TEST_MAKE_OS_MAIN(StartOS(0))
volatile int i = 0;

TASK(H1) {
	test_trace('1');
	TerminateTask();
}

TASK(H2) {
	static int i = 0;
	if (i == 0) {
		i++;
		test_trace('2');
	} else {
		test_trace('E');
		/* The testcase has finished, check the output */
		test_start_check();
		test_trace_assert((char *)"52:3{}E");
		test_finish();
		ShutdownMachine();
	}
	TerminateTask();
}

TASK(H3) {
	test_trace('3');
	GetResource(R234);
	test_trace('{');
	ActivateTask(H2);
	test_trace('}');
	ReleaseResource(R234);
	test_trace('T');
	TerminateTask();
}

TASK(H4) {
	test_trace('4');
	TerminateTask();
}

TASK(H5) {
	test_trace('5');
	ActivateTask(H2);
	test_trace(':');
	TerminateTask();
}
