/**
 * @file
 * @ingroup i386
 * @brief Default output streams
 */
#ifndef __OUTPUT_H__
#define __OUTPUT_H__

#include "arch/generic/ostream.h"

#ifndef FAIL
#if DEBUG

// debugging: print kout+debug on CGA
#include "cga.h"
extern CGA kout;
extern CGA debug;

#else // DEBUG

// not debugging: print kout on COM1, ignore debug
#include "serial.h"
extern Serial kout;
extern Null_Stream debug;

#endif // DEBUG

#else

extern Null_Stream kout;
extern Null_Stream debug;

#endif // FAIL


#endif // __OUTPUT_H__
