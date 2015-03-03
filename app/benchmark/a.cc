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
#include "fail/trace.h"

//extern "C" volatile uint32_t random_source =0 ;

DeclareTask(Handler11);
DeclareTask(Handler12);
DeclareTask(Handler13);

TEST_MAKE_OS_MAIN( StartOS(0) )

TASK(Handler11) {
    //test_trace(random_source);
    //test_trace(random_source);
    //test_trace(random_source);

	test_trace('a');
	ActivateTask(Handler12);
	test_trace('b');
	ActivateTask(Handler13);
	test_trace('c');
	TerminateTask();
}

TASK(Handler12) {
    //test_trace(random_source);
	test_trace('2');
	TerminateTask();
}

TASK(Handler13) {
	test_trace('3');
	TerminateTask();
}

void PreIdleHook() {
	test_finish();
	ShutdownMachine();
}
