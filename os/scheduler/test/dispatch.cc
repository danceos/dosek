/**
 * @file
 * @ingroup unit_tests
 * @test Test the dispatcher with 4 tasks
 */

#include "test/test.h"
#include "util/encoded.h"
#include "output.h"
#include "os/scheduler/thetasks.h"
#include "os/scheduler/scheduler.h"
using namespace os::scheduler;


// errors are injected in this namespace
namespace fail {
// integer value to track correct execution order
Encoded_Static<A0, 42> k;

// activate first task
void start(void)
{
	ActivateTask(t1);
}

};
using namespace fail;


// prepare tests
void test_prepare(void)
{
	// initialize integer
	k.encode(1, 0);
}

/**
 * @brief Runs dispatcher tests
 */
void test(void)
{
	//! @test Activate first task
	run_checkable_function(&start, k, 8359);
}

TASK(Handler11) {
	//serial << "Hello ";
	k = k * EC(43,2);
	k = k + EC(44,1);

	ActivateTask(t2);

	//serial << "!";
	k = k * EC(45,3);
	k = k + EC(46,2);

	ActivateTask(t3);

	//serial << " :)";
	k = k * EC(47,5);
	k = k + EC(48,3);

	TerminateTask();
}

TASK(Handler12) {
	//serial << "World";
	k = k * EC(49,7);
	k = k + EC(50,5);

	ChainTask(t4);
}

TASK(Handler13) {
	//serial << "X" << endl;
	k = k * EC(40,9);
	k = k + EC(41,7);

	TerminateTask();
}

TASK(Handler14) {
	//serial << "?";
	k = k * EC(39,2);
	k = k + EC(38,9);

	TerminateTask();
}
