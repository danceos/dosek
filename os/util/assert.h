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

// declared in helper.cc
extern "C" char color_assert_port;
#define COLOR_ASSERT_UNKOWN       0
#define COLOR_ASSERT_CFG_REGION   1
#define COLOR_ASSERT_SYSTEM_STATE 2

//! Runtime assert, print assertion if debugging, else causes trap
#if DEBUG
#include "output.h"
#define assert(x) { if((x)==0) { \
    kout << "ASSERT " << __FILE__ << ":" << __LINE__ << " " << __func__ << endl; \
    Machine::halt();}}

#define color_assert(x, color) { if((x)==0) {						\
			kout << "ASSERT " << __FILE__ << ":" << __LINE__ << " " << __func__ << endl; \
			color_assert_port = color;									\
			Machine::halt();											\
			}															\
	}

#else
#define assert(x) do { if((x)==0) Machine::debug_trap(); } while(0)
#define color_assert(x,color) do { \
		if((x) == 0) {													\
			color_assert_port = (color);								\
			Machine::debug_trap();										\
		}																\
	} while(0)

#endif

#ifdef FAIL
#undef assert
#define assert(x) color_assert(x, COLOR_ASSERT_UNKOWN)
#endif

//! Compile-time assert for constants as optimized by the compiler
#define pseudo_static_assert(A, T) { if(!(A)) { asm volatile( "assertion failed: " T ); } }

#endif /* __ASSERT_H__ */
