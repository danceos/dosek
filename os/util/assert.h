#ifndef __ASSERT_H__
#define __ASSERT_H__


/**
 * @file
 * @ingroup os
 * @brief Static and runtime asserts
 */

#include "machine.h"

#ifdef assert
#undef assert
#endif

//! Runtime assert, print assertion if debugging, else causes trap
#if DEBUG
#include "output.h"
#define assert(x) { if((x)==0) { \
    kout << "ASSERT " << __FILE__ << ":" << __LINE__ << " " << __func__ << endl; \
    Machine::halt();}}
#else
#define assert(x) do { if((x)==0) Machine::debug_trap(); } while(0)
// #define assert(x)
#endif

#endif /* __ASSERT_H__ */
