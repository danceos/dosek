/**
 * @file
 * @ingroup unit_tests
 * @test Test repeated alarn task activation while performing syscalls
 */

#include "test/test.h"
#include "util/encoded.h"
#include "output.h"
#include "machine.h"
#include "os/scheduler/thetasks.h"
#include "os/scheduler/scheduler.h"
#include "os/counter.h"
#include "os/alarm.h"
using namespace os::scheduler;

// debug serial print macro
#if DEBUG
#define DEBUGPRINT(STR) serial << STR << endl
#else
#define DEBUGPRINT(STR) do {} while(false)
#endif



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
	ActivateTaskC(t1.enc_id<3>());

	// should never come here
	Machine::unreachable();
}

volatile uint32_t count = 0; // task activations

TASK(Task1) {
	DEBUGPRINT("(1)");

	if(count == 0) {
		DEBUGPRINT("Arm timer");
		os::alarm0.setRelativeTime(10);
		os::alarm0.setArmed(true);
	}

	count++;

	DEBUGPRINT("Activate task 2");
	ActivateTask(t2);

	DEBUGPRINT("Chain task 2");
	ChainTask(t2);
}

TASK(Task2) {
	DEBUGPRINT("(2)");

	count++;

	DEBUGPRINT("Chain task 3");
	ChainTask(t3);
}

TASK(Task3) {
	DEBUGPRINT("(3)");

	while(true) {
		count++;

		DEBUGPRINT("Activate task 1");
		ActivateTask(t1);
	}
}

volatile uint32_t ticks = 0; // alarm task activations

TASK(Task4) {
	DEBUGPRINT("(4)");

	DEBUGPRINT("count: " << count);
	DEBUGPRINT("tick: " << ticks);

	if(++ticks < 100) {
		// run one test step
		step();

		// rearm with increasing interval
		DEBUGPRINT("Rearm timer");
		os::alarm0.setRelativeTime(ticks);
		os::alarm0.setArmed(true);
	} else {
		DEBUGPRINT("Finished");

		run_checkable_function(step, k, ticks+1);

		test_finish();

		// shutdown
		DEBUGPRINT("shutdown\n");
		Machine::shutdown();
	}

	TerminateTask();
}
