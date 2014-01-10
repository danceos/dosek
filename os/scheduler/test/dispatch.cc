/**
 * @file
 * @ingroup unit_tests
 * @test Test the dispatcher with 4 tasks
 */

#include "test/test.h"
#include "util/encoded.h"
#include "output.h"
#include "machine.h" // for shutdown
#include "os/scheduler/thetasks.h"
#include "os/scheduler/scheduler.h"
using namespace os::scheduler;

// debug serial print macro
#if DEBUG
#define DEBUGPRINT(STR) serial << STR
#else
#define DEBUGPRINT(STR) do {} while(false)
#endif

// errors are injected in this namespace
namespace fail {

// integer value to track correct execution order
Encoded_Static<A0, 42> k;

// these steps are executed in order by a correct OSEK system

forceinline void step1(void) {
	k = k * EC(43,2);
	k = k + EC(44,1);
}

forceinline void step2(void) {
	k = k * EC(49,7);
	k = k + EC(50,5);
}

forceinline void step3(void) {
	k = k * EC(39,2);
	k = k + EC(38,9);
}

forceinline void step4(void) {
	k = k * EC(45,3);
	k = k + EC(46,2);
}

forceinline void step5(void) {
	k = k * EC(47,5);
	k = k + EC(48,3);
}

forceinline void step6(void) {
	k = k * EC(40,9);
	k = k + EC(41,7);
}

};
using namespace fail;


// prepare tests
void test_prepare(void)
{
	// initialize test integer
	k.encode(1, 0);
}

/**
 * @brief Runs dispatcher tests
 */
void test(void)
{
	//! @test Activate first task
	ActivateTaskC(t1.enc_id<3>());
}

TASK(Task1) {
	DEBUGPRINT("HELLO");

	// step 1
	run_checkable_function(step1, k, 3);

	// activate and dispatch higher priority task 2
	ActivateTask(t2);

	DEBUGPRINT("!");

	// step 4
	run_checkable_function(step4, k, (((3*7)+5)*2+9)*3+2);

	// activate lower priority task 3 (no disptach)
	ActivateTask(t3);

	DEBUGPRINT(" :)");

	// step 5
	run_checkable_function(step5, k, ((((3*7)+5)*2+9)*3+2)*5+3);

	// terminate and switch to task 3
	TerminateTask();
}

TASK(Task2) {
	DEBUGPRINT("World");

	// step 2
	run_checkable_function(step2, k, (3*7)+5);

	// chain higher priority task 4
	ChainTask(t4);
}

TASK(Task3) {
	DEBUGPRINT("X\n");

	// step 6
	run_checkable_function(step6, k, 8359);

	// everything okay, finish test
	test_finish();

	// shutdown
	DEBUGPRINT("shutdown\n");
	Machine::shutdown();

	// would terminate to idle loop
	TerminateTask();
}

TASK(Task4) {
	DEBUGPRINT("?");

	// step 3
	run_checkable_function(step3, k, ((3*7)+5)*2+9);

	// terminate and return to task 1
	TerminateTask();
}
