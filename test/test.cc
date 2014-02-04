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

	char trace_table[256];
	unsigned char trace_table_idx = 0;
}