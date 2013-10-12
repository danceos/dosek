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

output_t kout;

/**
 *
 * @brief Serial output device
 * @todo Make hardware independent!
 */
Serial serial(Serial::COM1); 

#define EXPECTED_VALUES_MAX 10 
typedef unsigned int expected_value_t;


extern "C" {

	/**
     * @brief Untouched memory to store expected dynamic results.
     *
     * All variables in this structures will be protected by fail
	 *  during an fault injection experiment. Therefore it can't be
	 *  written by during the injection time
     */
	struct test_data_t {
		bool global_all_ok;     //!< If true on test exit, all tests passed
		int  positive_tests;    //!< Number of successful tests
		int experiment_number;  //!< Experiment number
		value_t encoded_storage; //!< ??
		expected_value_t expected_values[EXPECTED_VALUES_MAX]; //!< Expected values can be placed here.
	} test_data; //!< global instantiation


      //! user-supplied prepare function
	void test_prepare(void);

	//! user-supplied test functions
	void test(void);

	/**
     * @name FAIL* markers
     */
    //@{
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
	test_data.experiment_number++;
	test_data.positive_tests = 0;
	serial << "Test " << (unsigned) test_data.experiment_number << ": " << endl;
	#ifdef DEBUG
	kout.setcolor(CGA::WHITE, CGA::BLACK);
	kout << "[Test " << (unsigned) test_data.experiment_number << "]" << endl;
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
		serial << "POSITIVE" << endl;

		#ifdef DEBUG
		kout.setcolor(CGA::GREEN, CGA::BLACK);
		kout << "[POSITIVE]" << endl << endl;
		kout.setcolor(CGA::WHITE, CGA::BLACK);
		#endif
		test_data.positive_tests ++;
	} else {
		serial << "NEGATIVE " << real_value << (equal ? " != " : " == ") << expected_value << endl;
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
	test_data.expected_values[id] = value;
}

void test_expect_eq(unsigned char id, const expected_value_t expected_value) {
	test_equality(test_data.expected_values[id], expected_value, true);
}

void test_expect_ne(unsigned char id, const expected_value_t expected_value) {
	test_equality(test_data.expected_values[id], expected_value, false);
}

void test_assert(bool result) {
	test_equality(result, true, true);
}



void __test_positive_tests(int positive_tests, int sign) {
	int delta = test_data.positive_tests - positive_tests;
    if ((sign < 0 && delta < 0)
		|| (sign == 0 && delta == 0)
		|| (sign > 0 && delta > 0)) {
		serial << "SUCCESS " << test_data.experiment_number << endl;
		#ifdef DEBUG
		kout.setcolor(CGA::GREEN, CGA::BLACK);
		kout << "[SUCCESS] " << test_data.experiment_number << endl;
		kout.setcolor(CGA::WHITE, CGA::BLACK);
		#endif
    } else {
		test_data.global_all_ok = false;
		serial << "FAIL " << test_data.experiment_number << "(positive_tests = " << test_data.positive_tests << ")" << endl;
        #ifdef DEBUG
		kout.setcolor(CGA::RED, CGA::BLACK);
		serial << "[FAIL] " << test_data.experiment_number << "(positive_tests = " << test_data.positive_tests << ")" << endl;
		kout.setcolor(CGA::WHITE, CGA::BLACK);
		#endif

	}
	marker_stop_check();
	for (int i = 0; i < EXPECTED_VALUES_MAX; i++) {
		test_data.expected_values[i] = 0xAAAA5555;
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


// run one test
template<typename T>
void run_checkable_function(void (*testfun)(void), T& result_var, value_t expected) {
	test_expect_store(0, expected);
	test_data.encoded_storage = 0;

	/* Start the testcase (including marker_start() */
	test_start();
	testfun();
	test_start_check();

	/* Either the decoded value is equal to expected */
	test_expect_eq(0, result_var.decode());
	/* Or the check says: undecodable */
	test_assert(result_var.check() == false);
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

	test_data.global_all_ok = true;
	if (test_prepare != NULL) {
		test_prepare();
	}
	// run tests
	trace_start_marker();
	test();
	trace_end_marker();


	serial << "Tests finished: ";
	serial << (test_data.global_all_ok ? "ALL OK" : "some tests failed");
	serial << endl;


	#ifdef DEBUG
	kout.setcolor(CGA::RED, CGA::WHITE);
	kout << "CoRedOS halt" << endl;
	#endif

	#ifdef DEBUG
	asm("hlt"); // stop emulator, don't exit
	#else
	asm("int $0x03"); // triple fault, exit emulator
	#endif

	for(;;) {
		asm("nop");
	}
} 
