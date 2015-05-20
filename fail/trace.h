/**
 *  @defgroup trace Tracing
 *  @brief Tracing
 */


#include <stdint.h>
#include "util/inline.h"
#include "machine.h"
#include "output.h"

extern "C" {
    //! user-supplied test function
    noinline void test(void);

    //! test finish function
    noinline void test_finish();

    //! FAIL* checkpoint/tracing memory location
    __attribute__((weak)) volatile uint32_t fail_trace = 0;
}

inlinehint void test_start()
{
    #ifndef FAIL
    kout << "-- Trace start" << endl;
    #endif
}

noinline void test_finish()
{
    #ifndef FAIL
    kout << "-- Trace done" << endl;
    #else
    // to prevent compiler from optimizing the call
    Machine::nop();
    #endif
}

inlinehint void test_main(void)
{
    debug.setcolor(Color::RED, Color::WHITE);
    debug << "dOSEK start" << endl;
    debug.setcolor(Color::YELLOW, Color::BLACK);

    // run tests
    test();

    // finish tests
    test_finish();

    // halt system
    debug.setcolor(Color::RED, Color::WHITE);
    debug << "dOSEK halt" << endl;
    Machine::shutdown();
}

inlinehint void test_trace(uint32_t val)\
{
    fail_trace = val;

    #ifndef FAIL
	static uint32_t  i = 1;

    kout << "T " << (int)i++;
    kout << ": " <<  hex << val << dec << endl;
    #endif
}


#define TEST_MAKE_OS_MAIN(body) \
    void os_main(void) {        \
        test_main();            \
    }                           \
                                \
    void test() {               \
        test_start();           \
        body;                   \
    }                           \

