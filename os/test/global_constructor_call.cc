#include "test/test.h"

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
	bool res;

	test_start();
	res = g_consttest_23.getValue() == 23;
	test_result(res);

	test_start();
	res = g_consttest_42.getValue() == 42;
	test_result(res);
}

