/**
 *  @defgroup test Testing
 *  @brief Testing
 */

/**
 * @ingroup test
 * @defgroup unit_tests Unit Tests
 * @brief Small unit tests
 */


/**
 * @file
 * @ingroup unit_tests
 * @brief Basic functions for unit testing
 *
 * How to use test.h for unit tests
 * ================================
 *
 * A testcase can be defined by including the test.h header.
 * You can define `void test_prepare()` to do work before the experiment
 * (won't be traced).
 * 
 * The `void test(void)` function is called by the operating systems
 * main function. Everything that happens there will be included in
 * the fail trace afterwards.
 *
 * @warning This "header" file instantiates global objects.
 *          Do not include this header in multiple files!
 * 
 * Each testcase in the test functions has the following form:
 * 
 * * *Optionally* store dynamic test result:
 *   ~~~~~~~~~~~~~~{.c}
 *    // Store expected results (if dynamic)
 *    test_expect_store(0, expected_a);
 *    test_expect_store(1, exptected_b);
 *   ~~~~~~~~~~~~~~
 *
 * * Run test case:
 *   ~~~~~~~~~~~~~~{.c}
 *   // Start the testcase (injecting from here)
 *   test_start();
 *   run_my_super_dupper_test_function(&a, &b)
 *   // finish the testcase (injecting till here)
 *   int result = test_start_check();
 *   
 *   // Run n tests on the result:
 *   test_eq(result, 123);
 *   test_expect_eq(0, a);
 *   test_expect_eq(1, b);
 *   
 *   // Testcase is only positive when more than one condition holds
 *   test_positive_tests_gt(1);
 *   ~~~~~~~~~~~~~~
 */

#include "serial.h"
#include "output.h"
#include "os/encoded.h"
#include "os/os.h"

#define forceinline __inline__ __attribute__((always_inline))

#ifdef DEBUG
/**
 * @brief Console output device
 * Used for debugging tests
 * @todo Make hardware independent!
 */
output_t kout;
#endif

#ifndef FAIL
/**
 * @brief Serial output device
 * Used for CTest, but not FAIL to reduce binary
 * @todo Make hardware independent!
 */
Serial serial(Serial::COM1); 
#endif

#define EXPECTED_VALUES_MAX 10
typedef unsigned int expected_value_t;


extern "C" {
	/**
	 * @name FAIL* interface variables
	 * These are not changed during injection time as they are outside of fail namespace
	 */
	// @{

	//! encoded result value (result.vc) will be copied here 
	value_t encoded_storage;

	//! test check function detected error in result
	bool detected_error;

	//! all tests (so far) passed
	bool global_all_ok;

	//! number of positive checks in this test
	int positive_tests;

	//! number of current experiment
	int experiment_number;

	//! buffer for expected result values
	expected_value_t expected_values[EXPECTED_VALUES_MAX];

	// @}

	/**
	 * @name User supplied functions
	 */
	// @{
      	//! user-supplied prepare function
	void test_prepare(void);

	//! user-supplied test function
	void test(void);
	// @}

	/**
	 * @name FAIL* markers
	 */
	// @{
	void _marker_start() { };
	void (*marker_start)() = _marker_start;

	void _marker_start_check() { };
	void (*marker_start_check)() = _marker_start_check;

	void _marker_stop_check() { };
	void (*marker_stop_check)() = _marker_stop_check;

	void _trace_start_marker() { };
	void (*trace_start_marker)() = _trace_start_marker;

	void _trace_end_marker() { };
	void (*trace_end_marker)() = _trace_end_marker;
	// @}
}


inline
void test_start()
{
	// update global status variables
	experiment_number++;
	positive_tests = 0;

	#ifndef FAIL
	serial << "Test " << (unsigned) experiment_number << ": " << endl;
	#endif
	#ifdef DEBUG
	kout.setcolor(CGA::WHITE, CGA::BLACK);
	kout << "[Test " << (unsigned) experiment_number << "]" << endl;
	kout.setcolor(CGA::LIGHT_GREY, CGA::BLACK);
	#endif

	/* Set a marker for starting the test */
	marker_start();
}

inline
void test_start_check() {
	marker_start_check();
}


void test_equality(expected_value_t real_value, const expected_value_t expected_value, bool equal)
{
	if((equal && real_value == expected_value) || (!equal && real_value != expected_value)) {
		#ifndef FAIL
		serial << "POSITIVE" << endl;
		#endif
		#ifdef DEBUG
		kout.setcolor(CGA::GREEN, CGA::BLACK);
		kout << "[POSITIVE]" << endl << endl;
		kout.setcolor(CGA::WHITE, CGA::BLACK);
		#endif

		positive_tests++;
	} else {
		#ifndef FAIL
		serial << "NEGATIVE " << real_value << (equal ? " != " : " == ") << expected_value << endl;
		#endif
		#ifdef DEBUG
		kout.setcolor(CGA::RED, CGA::BLACK);
		serial << "[NEGATIVE] " << real_value << (equal ? " != " : " == ") << expected_value << endl;
		kout.setcolor(CGA::WHITE, CGA::BLACK);
		#endif
	}
}

void test_eq(expected_value_t real_value, const expected_value_t expected_value) {
	test_equality(real_value, expected_value, true);
}

void test_ne(expected_value_t real_value, const expected_value_t expected_value) {
	test_equality(real_value, expected_value, false);
}

/* Store and retrieve expected results */

void test_expect_store(unsigned char id, expected_value_t value) {
	expected_values[id] = value;
}

void test_expect_eq(unsigned char id, const expected_value_t expected_value) {
	test_equality(expected_values[id], expected_value, true);
}

void test_expect_ne(unsigned char id, const expected_value_t expected_value) {
	test_equality(expected_values[id], expected_value, false);
}

void test_assert(bool result) {
	test_equality(result, true, true);
}



void __test_positive_tests(int pos_tests, int sign) {
	int delta = positive_tests - pos_tests;
	if ((sign < 0 && delta < 0)
		|| (sign == 0 && delta == 0)
		|| (sign > 0 && delta > 0)) {
		#ifndef FAIL
		serial << "SUCCESS " << experiment_number << endl;
		#endif
		#ifdef DEBUG
		kout.setcolor(CGA::GREEN, CGA::BLACK);
		kout << "[SUCCESS] " << experiment_number << endl;
		kout.setcolor(CGA::WHITE, CGA::BLACK);
		#endif
	} else {
		global_all_ok = false;

		#ifndef FAIL
		serial << "FAIL " << experiment_number << "(positive_tests = " << positive_tests << ")" << endl;
		#endif
	        #ifdef DEBUG
		kout.setcolor(CGA::RED, CGA::BLACK);
		serial << "[FAIL] " << experiment_number << "(positive_tests = " << positive_tests << ")" << endl;
		kout.setcolor(CGA::WHITE, CGA::BLACK);
		#endif
	}

	marker_stop_check();

	for (int i = 0; i < EXPECTED_VALUES_MAX; i++) {
		expected_values[i] = 0xAAAA5555;
	}
}

void test_positive_tests_eq(int positive_tests) {
	__test_positive_tests(positive_tests, 0);
}

void test_positive_tests_lt(int positive_tests) {
	__test_positive_tests(positive_tests, -1);
}

void test_positive_tests_gt(int positive_tests) {
	__test_positive_tests(positive_tests, 1);
}


// run one test with unencoded result
// detectable can be set if the result value is known and error could be detected to set detected_error
// forceinline used to inline this into test() function to stay within allowed text region
// volatile used to prevent inlining of testfunction, which should stay separate
forceinline void run_checkable_function(void (* volatile testfun)(void), expected_value_t& result_var, value_t expected, bool detectable=false) {
	test_expect_store(0, expected);
	encoded_storage = 0;
	detected_error = false;

	/* Start the testcase (including marker_start() */
	test_start();
	testfun();
	test_start_check();
	encoded_storage = result_var;

	/* Chcek if result value is equal to expected */
	test_expect_eq(0, result_var);

	/* If the result value is known and the error would be detected set detected_error */
	if(detectable) detected_error = (result_var != expected);

	/* Check has to succeed */
	test_positive_tests_gt(0);
}

// run one test with encoded result
// forceinline used to inline this into test() function to stay within allowed text region
// volatile used to prevent inlining of testfunction, which should stay separate
template<typename T>
forceinline void run_checkable_function(void (* volatile testfun)(void), T& result_var, value_t expected) {
	test_expect_store(0, expected);
	encoded_storage = 0;
	detected_error = false;

	/* Start the testcase (including marker_start() */
	test_start();
	testfun();
	test_start_check();
	encoded_storage = result_var.vc;

	/* Either the decoded value is equal to expected */
	test_expect_eq(0, result_var.decode());
	/* Or the check says: undecodable */
	detected_error = !result_var.check();
	test_assert(detected_error == true);
	/* and at least one of the tests has to succeed */
	test_positive_tests_gt(0);
}

__attribute__((weak_import))
extern void test_prepare();

void os_main(void)
{
	#ifdef DEBUG
	kout.setcolor(CGA::RED, CGA::WHITE);
	kout << "CoRedOS start" << endl;
	kout.setcolor(CGA::LIGHT_GREY, CGA::BLACK);
	#endif

	// prepare tests
	global_all_ok = true;
	if (test_prepare != NULL) {
		test_prepare();
	}

	// run tests
	trace_start_marker();
	test();
	trace_end_marker();

	#ifndef FAIL
	serial << "Tests finished: ";
	serial << (global_all_ok ? "ALL OK" : "some tests failed");
	serial << endl;
	#endif

	// halt system
	#ifndef FAIL
	asm("int $0x03"); // triple fault, exit emulator
	#endif
	#ifdef DEBUG
	kout.setcolor(CGA::RED, CGA::WHITE);
	kout << "CoRedOS halt" << endl;
	asm("hlt"); // stop emulator, don't exit
	#endif

	for(;;) {
		asm("nop");
	}
} 
