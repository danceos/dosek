#include "serial.h"
#include "output.h"
#include "os/encoded.h"

output_t kout;
Serial serial(Serial::COM1);

extern "C" {

bool all_ok = true;

// FAIL* interface variables
char experiment_number = 0;
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
void test(void);

};

// run one test
template<typename T>
void run_test(void (*test)(void), T& result_var, value_t expected)
{
	// update global status variables
	experiment_number++;
	expected_result = expected;
	encoded_result = 0;

	serial << "Test " << (unsigned) experiment_number << ": ";
	#ifdef DEBUG
	kout.setcolor(CGA::WHITE, CGA::BLACK);
	kout << "[Test " << (unsigned) experiment_number << "]" << endl;
	kout.setcolor(CGA::LIGHT_GREY, CGA::BLACK);
	#endif

	// run the test
	test();

	// mark test completion
	subexperiment_marker_1();

	// analyze result
	detected_error = !result_var.check();
	encoded_result = result_var.vc;
	result = detected_error ? 0 : result_var.decode();

	// mark end of test
	subexperiment_end();

	// output success/failure
	if(detected_error || result == expected_result) {
		serial << "SUCCESS" << endl;

		#ifdef DEBUG
		kout.setcolor(CGA::GREEN, CGA::BLACK);
		kout << "[SUCCESS]" << endl << endl;
		#endif
	} else {
		all_ok = false;
		serial << "FAIL" << endl;
		#ifdef DEBUG
		kout.setcolor(CGA::RED, CGA::BLACK);
		kout << "[FAIL]" << endl << endl;
		#endif
	}

	#ifdef DEBUG
	kout.setcolor(CGA::WHITE, CGA::BLACK);
	#endif
}

void os_main(void)
{
	#ifdef DEBUG
	kout.setcolor(CGA::RED, CGA::WHITE);
	kout << "CoRedOS start" << endl;
	kout.setcolor(CGA::LIGHT_GREY, CGA::BLACK);
	#endif

	// prepare tests
	prepare();

	// tests ready
	trace_start_marker();

	// run tests
	test();

	// done, tracing can end here
	trace_end_marker();

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
