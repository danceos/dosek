//#define DEBUG 1

#include "serial.h"
#include "output.h"

output_t kout;
Serial serial(Serial::COM1);

class GlobalConstructorTester {
    int test;
public:

    GlobalConstructorTester() : test(23) {
    }

    GlobalConstructorTester( int x) {
        test = x;
    }

    int getValue() {
        return test;
    }
};

GlobalConstructorTester g_consttest_42(42);
GlobalConstructorTester g_consttest_23;

void os_main(void)
{
    #ifdef DEBUG
    kout.setcolor(CGA::RED, CGA::WHITE);
    kout << "CoRedOS start" << endl;
    kout.setcolor(CGA::LIGHT_GREY, CGA::BLACK);
    #endif

    bool all_ok = true;
    if(  g_consttest_23.getValue() != 23 )
    {
        all_ok = false;
    }

    if( g_consttest_42.getValue() != 42 )
    {
        all_ok = false;
    }

    serial << "Tests finished: ";
    serial << (all_ok ? "ALL OK" : "some tests failed");
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

    for(;;) {}
}

