/* \brief This file declares functions that can be included into a
   testcase to generate output for testing task activations */

#include "output.h"

static char trace_table[256];
static unsigned char trace_table_idx = 0;

void Trace(char chr) {
	if (trace_table_idx < 0xff)
		trace_table[trace_table_idx++] = chr;
}

void TraceDump(void) {
	for (unsigned char i = 0; i < trace_table_idx; i++) {
		kout << trace_table[i];
	}
}

void TraceAssert(char *expected) {
	int good = 1;
	for (unsigned char i = 0; i < trace_table_idx; i++) {
		if (expected[i] == 0) {
			kout << "too short" << endl;
			good = 0;
			break;
		}
		if (trace_table[i] != expected[i]) {
			kout << "too unqeual: " <<  trace_table[i] << " at " << (int)i <<endl;
			good = 0;
			break;
		}
	}

	kout << expected << endl;
	TraceDump();
	kout << endl;

	if (good) {
		kout << "SUCCESS ALL OK" << endl;
	} else {
		kout << "FAIL" << endl;
	}
}
