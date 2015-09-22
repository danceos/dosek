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

    noinline void test_trace_dump(void) {
        kout << "traced: ";
        for (unsigned char i = 0; i < trace_table_idx; i++) {
            kout << trace_table[i];
        }
    }

    noinline void test_trace_assert(const char *expected) {
        int good = 1;
        unsigned char count = 0;

        test_start_check();

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

        test_assert(good);
        test_positive_tests_gt(0);
    }

	void test_trace(char chr) {
		kout << chr << endl;
	    fail_trace = (uint32_t) chr;
		if (trace_table_idx < 0xff)
			trace_table[trace_table_idx++] = chr;
		//kout << trace_table[trace_table_idx-1] << endl;
	}

}
