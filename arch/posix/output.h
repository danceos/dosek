/**
 * @file
 * @ingroup posix
 * @brief Default output streams
 */
#ifndef __OUTPUT_H__
#define __OUTPUT_H__

#if DEBUG

// debugging: print kout+debug on stdout/stderr
#include "colorterminal.h"
extern ColorTerminal kout;
extern ColorTerminal debug;

#else // DEBUG

// not debugging: print kout on stdout, ignore debug
#include "colorterminal.h"
extern ColorTerminal kout;
extern Null_Stream debug;

#endif // DEBUG

#endif // __OUTPUT_H__
