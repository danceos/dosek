#include "serial.h"
#include "output.h"

output_t kout;
Serial serial(Serial::COM1);

extern "C" {

bool all_ok = true;
char experiment_number = 0;

// user-supplied test functions
void test(void);

};

void test_start()
{
	// update global status variables
	experiment_number++;

	serial << "Test " << (unsigned) experiment_number << ": ";
	#ifdef DEBUG
	kout.setcolor(CGA::WHITE, CGA::BLACK);
	kout << "[Test " << (unsigned) experiment_number << "]" << endl;
	kout.setcolor(CGA::LIGHT_GREY, CGA::BLACK);
	#endif
}

// output success/failure
void test_result(bool success)
{
	if(success) {
		serial << "SUCCESS" << endl;

		#ifdef DEBUG
		kout.setcolor(CGA::GREEN, CGA::BLACK);
		kout << "[SUCCESS]" << endl << endl;
		kout.setcolor(CGA::WHITE, CGA::BLACK);
		#endif
	} else {
		all_ok = false;
		serial << "FAIL" << endl;

		#ifdef DEBUG
		kout.setcolor(CGA::RED, CGA::BLACK);
		kout << "[FAIL]" << endl << endl;
		kout.setcolor(CGA::WHITE, CGA::BLACK);
		#endif
	}
}

void os_main(void)
{
	#ifdef DEBUG
	kout.setcolor(CGA::RED, CGA::WHITE);
	kout << "CoRedOS start" << endl;
	kout.setcolor(CGA::LIGHT_GREY, CGA::BLACK);
	#endif

	// run tests
	test();

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

	for(;;) {
		asm("nop");
	}
}
