/**
 * @file
 * @ingroup unit_tests
 * @test Test repeated alarn task activation while performing syscalls
 */

#include "test/test.h"
#include "util/encoded.h"
#include "output.h"
#include "machine.h"
#include "os/scheduler/scheduler.h"
#include "os/counter.h"
#include "os/alarm.h"
#include "os/os.h"

#include "os/test/generated-system.h"
using namespace os::scheduler;

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



// activate task 4 by alarm
os::Alarm os::alarm0(counter0, t4);

// prepare tests
void test_prepare(void)
{
	// initialize test integer
	k.encode(1, 0);
}

/**
 * @brief Run alarm tests
 */
void test(void)
{
	Machine::enable_interrupts();

	//! @test Activate first task
	ActivateTaskC_impl(t1.enc_id<3>());

	// should never come here
	Machine::unreachable();
}

volatile uint32_t count = 0; // task activations

TASK(Task1) {
	debug << "(1)" << endl;

	if(count == 0) {
		debug << "Arm timer" << endl;
		os::alarm0.setRelativeTime(10);
		os::alarm0.setArmed(true);
	}

	count++;

	debug << "Activate task 2" << endl;
	ActivateTask_impl(t2);

	debug << "Chain task 2" << endl;
	ChainTask_impl(t2);
}

TASK(Task2) {
	debug << "(2)" << endl;

	count++;

	debug << "Chain task 3" << endl;
	ChainTask_impl(t3);
}

TASK(Task3) {
	debug << "(3)" << endl;

	while(true) {
		count++;

		debug << "Activate task 1" << endl;
		ActivateTask_impl(t1);
	}
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
		os::alarm0.setRelativeTime(ticks);
		os::alarm0.setArmed(true);
	} else {
		debug << "Finished" << endl;

		run_checkable_function(step, k, ticks+1);

		test_finish(1);

		// shutdown
		debug << "shutdown\n" << endl;
		Machine::shutdown();
	}

	TerminateTask_impl();
}
