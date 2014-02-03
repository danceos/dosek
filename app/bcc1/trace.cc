/* \brief This file declares functions that can be included into a
   testcase to generate output for testing task activations */

#include "output.h"

char trace_table[256];
unsigned char trace_table_idx = 0;

void Trace(char chr) {
	if (trace_table_idx < 0xff)
		trace_table[trace_table_idx++] = chr;
}

void TraceDump(void) {
	kout << "traced: ";
	for (unsigned char i = 0; i < trace_table_idx; i++) {
		kout << trace_table[i];
	}
}

void TraceAssert(char *expected) {
	int good = 1;
	unsigned char count = 0;
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
	TraceDump();
	kout << endl;

	if (good) {
		kout << "SUCCESS ALL OK" << endl;
	} else {
		kout << "FAIL" << endl;
	}
}
