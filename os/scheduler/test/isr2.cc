/**
 * @file
 * @ingroup unit_tests
 * @test Test ISR2 and ISR1 activation
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


// lowest priority ISR2 triggering ISR1
ISR(66) {
	step5();

	LAPIC::trigger(70);

	LAPIC::send_eoi();
}

// middle priority ISR2 triggered by task 1
ISR(67) {
	step1();

	LAPIC::trigger(68);

	step3();

	LAPIC::trigger(66);

	step4();

	LAPIC::send_eoi();
}

// high priority ISR2 triggered by ISR 67
// should run after ISR 67 completes, as ISR are not preemptive
ISR(68) {
	step2();

	LAPIC::send_eoi();
}

// ISR2 activating task 2
ISR(69) {
	ActivateTaskC_impl(t2.enc_id<3>());

	LAPIC::send_eoi();
}

// ISR1 setting global variable
IRQ_HANDLER(70) {
	done = true;

	LAPIC::send_eoi();

	Machine::return_from_interrupt();
}

// new syscall to trigger interrupt using local APIC
// for now, any function can be called using syscall(),
// so it is easy to add this for this test.
noinline void trigger_syscall(uint8_t irq) {
	LAPIC::trigger(irq);
}

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

TASK(Task1) {
	DEBUGPRINT("(1)");

	// test ISR2+ISR1 chain
	DEBUGPRINT("Trigger ISR 67");
	syscall(trigger_syscall, 67, true);

	// check ISR1 has run
	assert(done);

	run_checkable_function(step6, k, 2681);

	// test ISR2 task activatin
	DEBUGPRINT("Trigger ISR 69");
	syscall(trigger_syscall, 69, true);

	// should never come here
	Machine::unreachable();
}

// task 2 is activated by ISR 69
TASK(Task2) {
	DEBUGPRINT("(2)");

	run_checkable_function(step7, k, 2681*2+5);

	DEBUGPRINT("finished");
	test_finish();

	DEBUGPRINT("shutdown\n");
	Machine::shutdown();
}
