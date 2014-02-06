/**
 * @file
 * @ingroup unit_tests
 * @test Test the dispatcher with 4 tasks
 */

#include "test/test.h"
#include "util/encoded.h"
#include "os.h"

DeclareTask(Task1);
DeclareTask(Task2);
DeclareTask(Task3);
DeclareTask(Task4);


void os_main() {
    test_main();
}

void test() {
   StartOS(0);
}

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

TASK(Task1) {
	debug << "HELLO";

	// step 1
	run_checkable_function(step1, k, 3);

	// activate and dispatch higher priority task 2
	ActivateTask(Task2);

	debug << "!";

	// step 4
	run_checkable_function(step4, k, (((3*7)+5)*2+9)*3+2);

	// activate lower priority task 3 (no disptach)
	ActivateTask(Task3);

	debug << " :)";

	// step 5
	run_checkable_function(step5, k, ((((3*7)+5)*2+9)*3+2)*5+3);

	// terminate and switch to task 3
	TerminateTask();
}

TASK(Task2) {
	debug << "World";

	// step 2
	run_checkable_function(step2, k, (3*7)+5);

	// chain higher priority task 4
	ChainTask(Task4);
}

TASK(Task3) {
	debug << "X" << endl;

	// step 6
	run_checkable_function(step6, k, 8359);

	// everything okay, finish test
	test_finish(6);

	// shutdown
	debug << "shutdown" << endl;
	Machine::shutdown();

	// would terminate to idle loop
	TerminateTask();
}

TASK(Task4) {
	debug << "?";

	// step 3
	run_checkable_function(step3, k, ((3*7)+5)*2+9);

	// terminate and return to task 1
	TerminateTask();
}
