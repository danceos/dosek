#ifndef __BCC1_TRACE
#define  __BCC1_TRACE


/* \brief This file declares functions that can be included into a
   testcase to generate output for testing task activations */


/* \brief Add a trace marker */
void Trace(char chr);

/* \brief dump the trace to kout */
void TraceDump(void);

/* \brief compare the trace to an expected value */
void TraceAssert(char *expected);

#endif
