/**
 * @file
 * @ingroup scheduler
 * @brief The task list
 */

#ifndef __TASKLIST_H__
#define __TASKLIST_H__

#include <stdint.h>
#include "task.h"
#include "util/assert.h"
#include "util/encoded.h"

namespace os {
namespace scheduler {

/* Simpler array based task queue */
class TaskListStatic {
public:
	// Effect: (a,x) = max{((a,x), (b,y)} with (a,x) <= (b,y) <=> a <= b
	// subtracts signature B0 from a,x and adds signature sig to catch lost updates
	template<typename CP, typename OP, typename CI, typename OI>
	forceinline void updateMax(B_t& sigPrio, B_t& sigId, const B_t sig,
			CP * const current_prio, const OP & other_prio,
			CI * const current_id, const OI & other_id) const {
		pseudo_static_assert(other_prio.getB() > sigPrio,  "signature of b must be greater than signature of a");
		asm_label("updateMax");

		// unencoded comparison
		bool result;
		result = (current_prio->vc - sigPrio) <= (other_prio.vc - other_prio.getB());

		// encoded check of comparison
		// a>b  => diff = 2^32 - (a.vc - b.vc)
		// a<=b => diff = b.vc - a.vc
		value_coded_t diff = other_prio.vc - current_prio->vc;
		static const volatile A_t ta = CP::A; // prevent % -> *,>>,+ optimization
		value_coded_t sigCond = diff % ta;
		const value_coded_t sigPos = other_prio.getB() - sigPrio;
		const value_coded_t sigNeg = (CP::MAXMODA + sigPos) % CP::A;
		pseudo_static_assert(sigPos != sigNeg, "sigPos and sigNeg must differ");

		if(result) {
			current_prio->vc = sigPrio + (other_prio.vc - other_prio.getB()) + sig - sigPos;
			current_id->vc = sigId + other_id.vc + sig;
		} else {
			current_prio->vc += (sigPos - sigNeg) + (sig - sigPos);
			current_id->vc += (sigPos - sigNeg) + other_id.getB() + sig;
		}

		// return finished control flow signature
		current_prio->vc += sigCond;
		current_id->vc += sigCond;

		//return sig + sigCond;
		sigPrio += sig;
		sigId += sig + sigPos + other_id.getB();
	}

	// Effect: a = max{a, b} with a <= b
	// subtracts signature B0 from a,x and adds signature B1 to catch lost updates
	template<B_t B0, B_t B1, typename T, typename S>
	forceinline value_coded_t updateMax(T& a, const S& b) const {

		// control flow signature
		value_coded_t result;

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
			// a=b with added signature B1
			a.vc = b.vc + (T::B - S::B) + B1;

			// set control flow signature (expected: sigCond == sigPos)
			result += (T::A - 1) + B1;
		} else {
			// remove old B-1, add new B signature to "unmodified" a,x
			a.vc = a.vc - B0 + B1;

			// set control flow signature (expected: sigCond == sigNeg)
			result += (sigPos - sigNeg) + B1;
		}

		// return finished control flow signature
		result += sigCond;
		return result;
	}


	template<typename T, typename S>
	static constexpr value_coded_t updateMax_signature(value_coded_t B1, __attribute__ ((unused)) T& prio, __attribute__ ((unused)) S& task) {
		return (S::B - T::B + B1) % S::A;
	}

};

}; // namespace scheduler
}; // namespace os

#endif // __TASKLIST_H__
