/**
 * @file
 * @ingroup unit_tests
 * @test Test alarn task activation
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



// activate task 2 by alarm
os::Alarm os::alarm0(counter0, t2);

volatile uint32_t ticks = 0; // alarm task activations
volatile bool running = false; // track if Task2 is already/still running

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

TASK(Task1) {
	DEBUGPRINT("(1)");

	DEBUGPRINT("Arm timer");
	os::alarm0.setCycleTime(10);
	os::alarm0.setRelativeTime(100);
	os::alarm0.setArmed(true);

	DEBUGPRINT("Terminate task 1");
	TerminateTask();
}

TASK(Task2) {
	// check for double activations by fast alarm cycle
	if(!running) {
		running = true;
	} else {
		Machine::debug_trap();
	}

	DEBUGPRINT("(2)");
	DEBUGPRINT("tick: " << ticks);
	DEBUGPRINT("alarm time: " << os::alarm0.getAbsoluteTime());

	// count and test
	ticks++;
	run_checkable_function(step, k, ticks+1);

	if(ticks == 3) {
		// use short cycle to test alarm trigger while task is still running
		os::alarm0.setCycleTime(1);
	} else if(ticks == 6) {
		// done
		DEBUGPRINT("finished");
		test_finish();

		DEBUGPRINT("shutdown\n");
		Machine::shutdown();
	}

	running = false;
	TerminateTask();
}
