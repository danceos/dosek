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

#include <stdint.h>
#include "util/encoded.h"
#include "util/inline.h"
#include "output.h"

#define EXPECTED_VALUES_MAX 10
typedef unsigned int expected_value_t;


extern "C" {
	/**
	 * @name FAIL* interface variables
	 * These are not changed during injection time as they are outside of fail namespace
	 */
	// @{

	//! encoded result value (result.vc) will be copied here
	extern value_t encoded_storage;

	//! test check function detected error in result
	extern bool detected_error;

	//! all tests (so far) passed
	extern bool global_all_ok;

	//! number of positive checks in this test
	extern	int positive_tests;

	//! number of current experiment
	extern	int experiment_number;

	//! buffer for expected result values
	extern expected_value_t expected_values[EXPECTED_VALUES_MAX];

	//! buffer for task activation records
	extern char trace_table[256];

	//! index for trace_table
	extern unsigned char trace_table_idx;

	// @}

	/**
	 * @name User supplied functions
	 */
	// @{
      	//! user-supplied prepare function
	void test_prepare(void);

	//! user-supplied test function
	noinline void test(void);
	// @}

	/**
	 * @name FAIL* markers
	 */
	// @{
	extern void (*marker_start)();
	extern void (*marker_start_check)();
	extern void (*marker_stop_check)();
	extern void (*trace_start_marker)();
	extern void (*trace_end_marker)();
	// @}
}


inlinehint void test_start();
inlinehint void test_start_check();

void test_equality(expected_value_t real_value, const expected_value_t expected_value, bool equal);

void test_eq(expected_value_t real_value, const expected_value_t expected_value);
void test_ne(expected_value_t real_value, const expected_value_t expected_value);

/* Store and retrieve expected results */
void test_expect_store(unsigned char id, expected_value_t value);
void test_expect_eq(unsigned char id, const expected_value_t expected_value);
void test_expect_ne(unsigned char id, const expected_value_t expected_value);

/* Assert one boolean value */
void test_assert(bool result);


void test_positive_tests_eq(int positive_tests);
void test_positive_tests_lt(int positive_tests);
void test_positive_tests_gt(int positive_tests);


// run one test with unencoded result
// detectable can be set if the result value is known and error could be detected to set detected_error
// forceinline used to inline this into test() function to stay within allowed text region
// volatile used to prevent inlining of testfunction, which should stay separate
inlinehint void run_checkable_function(void (* volatile testfun)(void), expected_value_t& result_var, value_t expected, bool detectable=false);

// run one test with encoded result
// forceinline used to inline this into test() function to stay within allowed text region
// volatile used to prevent inlining of testfunction, which should
// stay separate
// run one test with encoded result
// forceinline used to inline this into test() function to stay within allowed text region
// volatile used to prevent inlining of testfunction, which should stay separate
template<typename T>
void run_checkable_function(void (* volatile testfun)(void), T& result_var, value_t expected) {
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

void test_init(void);
void test_finish(int tests=0);

void test_main(void);

/* \brief Add a trace marker */
void test_trace(char chr);

/* \brief dump the trace to kout */
void test_trace_dump(void);

/* \brief compare the trace to an expected value */
void test_trace_assert(char *expected);


#define TEST_MAKE_OS_MAIN(body) \
	void os_main(void) {		\
		test_main();			\
	}							\
								\
	void test() {				\
		test_start();			\
		body;					\
	}							\

