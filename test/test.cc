#include "test/test.h"

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
	noinline void test(void);
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

inlinehint void test_start()
{
	// update global status variables
	experiment_number++;
	positive_tests = 0;

	kout.setcolor(Color::WHITE, Color::BLACK);
	kout << endl << "Test " << (unsigned) experiment_number << ": " << endl;
	kout.setcolor(Color::YELLOW, Color::BLACK);

	/* Set a marker for starting the test */
	marker_start();
}

inlinehint void test_start_check() {
	marker_start_check();
}

void test_equality(expected_value_t real_value, const expected_value_t expected_value, bool equal)
{
	if((equal && real_value == expected_value) || (!equal && real_value != expected_value)) {
		kout.setcolor(Color::GREEN, Color::BLACK);
		kout << "  +" << endl;
		kout.setcolor(Color::WHITE, Color::BLACK);

		positive_tests++;
	} else {
		kout.setcolor(Color::RED, Color::BLACK);
		kout << "  -[" << real_value << (equal ? " != " : " == ") << expected_value << "]" << endl;
		kout.setcolor(Color::WHITE, Color::BLACK);
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

		kout.setcolor(Color::GREEN, Color::BLACK);
		kout << "SUCCESS " << experiment_number << endl;
		kout.setcolor(Color::WHITE, Color::BLACK);
	} else {
		global_all_ok = false;

		kout.setcolor(Color::RED, Color::BLACK);
		kout << "FAIL " << experiment_number << "(positive_tests = " << positive_tests << ")" << endl;
		kout.setcolor(Color::WHITE, Color::BLACK);
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
forceinline void run_checkable_function(void (* volatile testfun)(void), expected_value_t& result_var, value_t expected, bool detectable) {
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


__attribute__((weak_import))
extern void test_prepare();

void test_init(void) {
	// prepare tests
	global_all_ok = true;
	if (test_prepare != 0) {
		test_prepare();
	}

	// run tests
	trace_start_marker();
}



void test_finish(int tests) {
	trace_end_marker();

	if((tests > 0) && (tests != experiment_number)) {
		kout << "INCORRECT NUMBER of tests run: ";
		kout << dec << experiment_number << " instead of " << tests;
		kout << endl;
	} else {
		kout << "Tests finished: ";
		kout << (global_all_ok ? "ALL OK" : "some tests failed");
		kout << endl;
	}
}



void test_main(void)
{
	debug.setcolor(Color::RED, Color::WHITE);
	debug << "CoRedOS start" << endl;
	debug.setcolor(Color::YELLOW, Color::BLACK);

	// prepare tests
	test_init();

	// run tests
	test();

	// finish tests
	test_finish();

	// halt system
	debug.setcolor(Color::RED, Color::WHITE);
	debug << "CoRedOS halt" << endl;
	Machine::shutdown();
}

char trace_table[256];
unsigned char trace_table_idx = 0;

void test_trace(char chr) {
	if (trace_table_idx < 0xff)
		trace_table[trace_table_idx++] = chr;
}

void test_trace_dump(void) {
	kout << "traced: ";
	for (unsigned char i = 0; i < trace_table_idx; i++) {
		kout << trace_table[i];
	}
}

void test_trace_assert(char *expected) {
	int good = 1;
	unsigned char count = 0;
	for (; expected[count] != 0 && count < 255; count++) {}
	if (count != trace_table_idx) {
		kout << "trace length != expected " << (int) trace_table_idx << endl;
		good = 0;
	} else {
		for (unsigned char i = 0; i < trace_table_idx; i++) {
			if (trace_table[i] != expected[i]) {
				kout << "too unqeual: " <<  trace_table[i] << " at " << (int)i <<endl;
				good = 0;
				break;
			}
		}
	}

	kout << "expect: " << expected << endl;
	test_trace_dump();
	kout << endl;

	if (good) {
		kout << "SUCCESS ALL OK" << endl;
	} else {
		kout << "FAIL" << endl;
	}
}
