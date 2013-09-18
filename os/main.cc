#include "cga.h"

extern "C" {

char experiment_number;
//char detected_error;
//uint32_t result;

void _subexperiment_end() { };
void (*subexperiment_end)() = _subexperiment_end;

void _subexperiment_marker_1() { };
void (*subexperiment_marker_1)() = _subexperiment_marker_1;

void _trace_start_marker() { };
void (*trace_start_marker)() = _trace_start_marker;

void _trace_end_marker() { };
void (*trace_end_marker)() = _trace_end_marker;

}

#include "tests.h"

#define DEBUG
#ifdef DEBUG
#define debug(...) printf(__VA_ARGS__)
#else
#define debug(...) do {} while(0)
#endif

CGA kout;

void os_main(void) {
	kout << "START\n\n";

	setup();

	trace_start_marker();

	experiment_number = 1;
	subexperiment_marker_1();
	test1();
	subexperiment_end();

/*
	experiment_number = 2;
	subexperiment_marker_1();
	correct_action = test2();
	subexperiment_end();

	experiment_number = 3;
	subexperiment_marker_1();
	correct_action = test3();
	subexperiment_end();
*/

	trace_end_marker();

	kout << "\n\nEND";

	for(;;) {}
}

