/**
 * @file
 * @ingroup unit_tests
 * @test Test repeated alarn task activation while performing syscalls
 */

#include "test/test.h"
#include "util/encoded.h"
#include "os/os.h"

DeclareTask(Task1);
DeclareTask(Task2);
DeclareTask(Task3);
DeclareTask(Task4);
DeclareCounter(C1);
DeclareAlarm(A0);

void os_main() {
    test_main();
}

void test() {
   StartOS(0);
}


// errors are injected in this namespace
namespace fail {

// integer value to track test execution
Encoded_Static<A0, 42> k;

// test step: increment encoded value
forceinline void step(void) {
	k = k + EC(44,1);
}

};
using namespace fail;



// prepare tests
void test_prepare(void)
{
	// initialize test integer
	k.encode(1, 0);
}

volatile uint32_t count = 0; // task activations

TASK(Task1) {
	debug << "(1)" << endl;

	if(count == 0) {
		debug << "Arm timer" << endl;
		// FIXME: Implement Alarm system calls
		// Machine::disable_interrupts();
		// os::alarm0.setRelativeTime(10);
		// os::alarm0.setArmed(true);
		// os::alarm0.setCycleTime(10);
		// Machine::enable_interrupts();
	}

	count++;

	debug << "Activate task 2" << endl;
	ActivateTask(Task2);

	debug << "Chain task 2" << endl;
	ChainTask(Task2);
}

TASK(Task2) {
	debug << "(2)" << endl;

	count++;

	debug << "Chain task 3" << endl;
	ChainTask(Task3);
}

TASK(Task3) {
	debug << "(3)" << endl;

	while(true) {
		count++;

		debug << "Activate task 1" << endl;
		ActivateTask(Task1);
	}
	TerminateTask();
}

volatile uint32_t ticks = 0; // alarm task activations

TASK(Task4) {
	debug << "(4)" << endl;

	debug << "count: " << count << endl;
	debug << "tick: " << ticks << endl;

	if(++ticks < 100) {
		// run one test step
		step();

		// rearm with increasing interval
		debug << "Rearm timer" << endl;
		// Machine::disable_interrupts();
		// os::alarm0.setCycleTime(ticks);
		// Machine::enable_interrupts();
	} else {
		Machine::disable_interrupts();
		debug << "Finished" << endl;

		run_checkable_function(step, k, ticks+1);

		// os::alarm0.setCycleTime(0);

		test_finish(1);

		// shutdown
		debug << "shutdown\n" << endl;
		Machine::shutdown();
	}

	TerminateTask();
}
