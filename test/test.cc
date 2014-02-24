#include "test/test.h"

extern "C" {
	bool global_all_ok;
	int positive_tests;
	int experiment_number;
	expected_value_t expected_values[EXPECTED_VALUES_MAX];
	bool interrupts_suspended = false;
    char trace_table[256];
    unsigned char trace_table_idx = 0;

    volatile uint32_t fail_trace = 0;

	void test_prepare(void);

	noinline void test(void);

    noinline void test_finish(int tests) {
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
}
