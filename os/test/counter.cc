/**
 * @file
 * @ingroup unit_tests
 * @test Test counters
 */

#include "test/test.h"
#include "output.h"
#include "machine.h"
#include "os/counter.h"

extern os::Counter os::counter0;

/**
 * @brief Run counter test
 */
void test(void)
{
	// enable interrupts for counter timer
	Machine::enable_interrupts();



	// Test 1: wait 1000 ticks while CPU is running
	test_start();

	while(os::counter0.getValue() < 1000) Machine::nop();

	test_start_check();

	uint32_t val = os::counter0.getValue();
	test_assert((val >= 1000) && (val < 1100));

	test_positive_tests_eq(1);



	// Test 2: wait 1000 ticks while CPU is halted
	test_start();

	// passive wait 1000 ticks
	while(os::counter0.getValue() < 2000) Machine::halt();

	test_start_check();

	val = os::counter0.getValue();
	test_assert((val >= 2000) && (val < 2100));

	test_positive_tests_eq(1);
}