/**
 * @file
 * @ingroup unit_tests
 * @test Test the execution of global constructors.
 */

#include "os/os.h"
#include "test/test.h"

void os_main(void) {
	test_main();
}

class GlobalConstructorTester {
    int test;

public:
    GlobalConstructorTester() : test(23)
    {
    }

    GlobalConstructorTester(int testvalue)
    {
        test = testvalue;
    }

    int getValue()
    {
        return test;
    }
};

GlobalConstructorTester g_consttest_42(42);
GlobalConstructorTester g_consttest_23;

// run tests
void test(void)
{
	test_start();
	unsigned int result = g_consttest_23.getValue();
	test_start_check();
	test_eq(result, 23);
	test_positive_tests_eq(1);


	test_start();
	result = g_consttest_42.getValue();
	test_start_check();
	test_eq(result, 42);
	test_positive_tests_eq(1);
}

