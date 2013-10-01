#include "test.h"
#include "os/encoded.h"

extern "C" {

// FAIL* interface variables
char detected_error = false;
char result = -1;
char expected_result = -1;
value_t encoded_result = -1;

// FAIL* markers
void _subexperiment_end() { };
void (*subexperiment_end)() = _subexperiment_end;

void _subexperiment_marker_1() { };
void (*subexperiment_marker_1)() = _subexperiment_marker_1;

void _trace_start_marker() { };
void (*trace_start_marker)() = _trace_start_marker;

void _trace_end_marker() { };
void (*trace_end_marker)() = _trace_end_marker;

// user-supplied test functions
void prepare(void);
void do_test(void);

};

// run one test
template<typename T>
void run_test(void (*testfun)(void), T& result_var, value_t expected)
{
	test_start();

	// update global status variables
	expected_result = expected;
	encoded_result = 0;

	// run the test
	testfun();

	// mark test completion
	subexperiment_marker_1();

	// analyze result
	detected_error = !result_var.check();
	encoded_result = result_var.vc;
	result = detected_error ? 0 : result_var.decode();

	// mark end of test
	subexperiment_end();

	// output success/failure
	test_result(detected_error || result == expected_result);
}

void test(void)
{
	// prepare tests
	prepare();

	// tests ready
	trace_start_marker();

	// run tests
	do_test();

	// done, tracing can end here
	trace_end_marker();
}

