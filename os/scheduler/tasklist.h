#ifndef __TASKLIST_H__
#define __TASKLIST_H__


/**
 * @file
 * @ingroup scheduler
 * @brief The task list
 */


#ifndef DEBUG
#define DEBUG 0
#endif

#include <stdint.h>
#include "output.h"
#include "task.h"
#include "util/assert.h"
#include "util/encoded.h"

namespace os {
namespace scheduler {

/* Simpler array based task queue */
class TaskListStatic {
public:
	// idle task id/priority
	static constexpr auto idle_id = EC(13,0);
	static constexpr auto idle_prio = EC(12,0);


	// Effect: (a,x) = max{((a,x), (b,y)} with (a,x) <= (b,y) <=> a <= b
	// subtracts signature B0 from a,x and adds signature B1 to catch lost updates
	template<B_t B0, B_t B1, typename T, typename S, typename U, typename V>
	forceinline value_coded_t updateMax(T& a, const S& b, U& x, const V& y) const {
		TAssert(S::B > T::B);

		// control flow signature
		value_coded_t result;

		// check correct a,x after subtracting signature B0
		assert((a.vc - B0 - T::B - a.D) % T::A == 0);
		assert((x.vc - B0 - U::B - x.D) % U::A == 0);

		// unencoded comparison
		result = ((a.vc - B0) - T::B) <= (b.vc - S::B);

		// encoded check of comparison
		value_coded_t diff = b.vc - (a.vc - B0); // this>t  => diff = 2^m - (vc - t.vc)
		                                         // this<=t => diff = t.vc - vc
		static const volatile A_t ta = T::A; // prevent % -> *,>>,+ optimization
		value_coded_t sigCond = diff % ta;
		const value_coded_t sigPos = S::B - T::B;
		const value_coded_t sigNeg = (T::MAXMODA + sigPos) % T::A;

		if(result) {
			// FIXME: if(DEBUG) kout << "< ";

			// a=b, x=y with added signature B1
			a.vc = b.vc + (T::B - S::B) + B1;
			x.vc = y.vc + (U::B - V::B) + B1;

			// set control flow signature (expected: sigCond == sigPos)
			result += (T::A - 1) + B1; // + (S::B - T::B);
		} else {
			// if(DEBUG) kout << "> ";

			// remove old B-1, add new B signature to "unmodified" a,x
			a.vc = a.vc - B0 + B1;
			x.vc = x.vc - B0 + B1;

			// set control flow signature (expected: sigCond == sigNeg)
			result += (sigPos - sigNeg) + B1; // + (S::B - T::B);
		}

		// return finished control flow signature
		result += sigCond;
		return result;
	}

	// DEBUGGING
	void print() const {
		//kout << "(" << task1.decode() << "), ";
		//kout << "(" << task2.decode() << "), ";
		//kout << "(" << task3.decode() << "), ";
		//kout << "(" << task4.decode() << ")" << endl;
	}
};

}; // namespace scheduler
}; // namespace os

#endif // __TASKLIST_H__
