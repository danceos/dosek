#include "os.h"
#include "test/test.h"

DeclareTask(H1);
DeclareTask(H2);
DeclareTask(H3);
DeclareAlarm(A1);
DeclareCounter(C1);
DeclareAlarm(A2);
DeclareCounter(C2);


TEST_MAKE_OS_MAIN(StartOS(0))

TASK(H1) {
    test_trace('1');
    TerminateTask();
}

TASK(H2) {
    test_trace('2');

    test_trace_assert("312");
    test_finish();
    ShutdownMachine();
    TerminateTask();
}

TASK(H3) {
	// We insert the nops here to get a distinction between the system calls in the fail trace
    test_trace('3');
    SetRelAlarm(A1, 1, 0);
	Machine::nop();
    SetRelAlarm(A2, 1, 0);
	Machine::nop();
    TerminateTask();
}
