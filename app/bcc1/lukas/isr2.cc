/**
 * @file
 * @ingroup unit_tests
 * @test Test ISR2 and ISR1 activation
 */

#include "test/test.h"
#include "os/os.h"

DeclareTask(Task1);
DeclareTask(Task2);
DeclareTask(Task3);
DeclareTask(Task4);


void os_main(void) {
	test_main();
}

void test() {
	StartOS(0);
}

// errors are injected in this namespace
namespace fail {

// integer value to track test execution
Encoded_Static<A0, 42> k;

// these steps are executed in order by a correct OSEK system

forceinline void step1(void) {
	kout << "1";
	k = k * EC(43,2);
	k = k + EC(44,1);
}

forceinline void step2(void) {
	kout << "2";

	k = k * EC(49,7);
	k = k + EC(50,5);
}

forceinline void step3(void) {
	kout << "3";

	k = k * EC(39,2);
	k = k + EC(38,9);
}

forceinline void step4(void) {
	kout << "4";

	k = k * EC(45,3);
	k = k + EC(46,2);
}

forceinline void step5(void) {
	kout << "5";

	k = k * EC(47,4);
	k = k + EC(48,3);
}

forceinline void step6(void) {
	k = k * EC(40,2);
	k = k + EC(41,3);
}

forceinline void step7(void) {
	k = k * EC(3,2);
	k = k + EC(5,5);
}

};
using namespace fail;

volatile bool done = false;


ISR2(ISR37) {
	step4();

	Machine::trigger_interrupt_from_user(39);
}

ISR2(ISR38) {
	step1();


	step2();

	// ISRs are no preemtable
	Machine::trigger_interrupt_from_user(37);

	step3();
}

ISR2(ISR39) {
	done = 1;
	step5();
}

ISR2(ISR40) {
	ActivateTask(Task2);
}



TASK(Task1) {
	k.encode(1, 0);
	debug << "(1)" << endl;

	// test ISR2+ISR1 chain
	debug << "Trigger ISR 67" << endl;
	Machine::trigger_interrupt_from_user(38);

	// check ISR1 has run
	debug << "done: " << done << endl;

	run_checkable_function(step6, k, 1489);

	// test ISR2 task activatin
	debug << "Trigger ISR 69" << endl;
	Machine::trigger_interrupt_from_user(40);

	TerminateTask();
}

// task 2 is activated by ISR 69
TASK(Task2) {
	debug << "(2)" << endl;

	run_checkable_function(step7, k, 1489*2+5);

	debug << "finished" << endl;
	test_finish(2);

	debug << "shutdown\n" << endl;
	Machine::shutdown();
	TerminateTask();
}
