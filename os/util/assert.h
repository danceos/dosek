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
#define assert(x) { if((x)==0) Machine::debug_trap(); }
#endif

//! Static assert for compile-time checks
template <bool B>
struct tAssert
{
};

template<> struct tAssert<true>
{
    static void Assert() {};
};

#define TAssert(a) {const bool b = (const bool) (a); tAssert<b>::Assert();}

#endif /* __ASSERT_H__ */
