/*
 * Assert.h
 *
 *  Created on: 13.05.2013
 *      Author: ulbrich
 */

#ifndef TASSERT_H_
#define TASSERT_H_

//#include <assert.h>

// #ifdef ASSERT
// #warning ASSERT is already defined.
// #undef ASSERT
// #endif

// inline void ASSERT(bool assertion)
// {
//     if (!assertion)
// 	    assert(assertion);
// }

template <bool B>
struct tAssert
{
};

template<> struct tAssert<true>
{
    static void Assert() {};
};

#define TAssert(a) {const bool b = (const bool) (a); tAssert<b>::Assert();}

#endif /* TASSERT_H_ */
