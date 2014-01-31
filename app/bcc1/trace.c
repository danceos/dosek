/* \brief This file declares functions that can be included into a
   testcase to generate output for testing task activations */

char trace_table[256];
unsigned char trace_table_idx = 0;

void Trace(char chr) {
	if (trace_table_idx < 0xff)
		trace_table[trace_table_idx++] = chr;
}

void TraceDump(void) {
	for (unsigned char i = 0; i < trace_table_idx; i++) {
		putchar(trace_table[i]);
	}
}

void TraceAssert(char *expected) {
	int good = 1;
	if (strlen(expected) != trace_table_idx) {
		good = 0;
	} else {
		for (unsigned char i = 0; i < trace_table_idx; i++) {
			if (trace_table[i] != expected[i]) {
				good = 0;
				break;
			}
		}
	}

	putstring(expected);
	putchar('\n');
	TraceDump();
	putchar('\n');

	if (good) {
		putstring("SUCCESS ALL OK\n");
	} else {
		putstring("FAIL\n");
	}
}
