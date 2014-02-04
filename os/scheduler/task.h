#ifndef __TASK_H__
#define __TASK_H__
/**
 *  @ingroup os
 *  @defgroup scheduler The Scheduler
 *  @brief This module provides scheduling functions
 */


/**
 * @file
 * @ingroup scheduler
 * @brief The task handler
 */
#include "os/util/encoded.h"
#include "os/util/inline.h"

namespace arch {
    struct TCB;
};

namespace os {
namespace scheduler {

/**
 * The basic task class
 * */
class Task {
public:
	typedef uint8_t id_t;
	typedef uint8_t prio_t;

	// task ID
	const id_t id;
	template<typename T> constexpr T enc_id() const {
		return T(id);
	}
	template<B_t B> constexpr Encoded_Static<A0, B> enc_id() const {
		return Encoded_Static<A0, B>(id);
	}

	// static priority
	const prio_t prio;
	template<typename T> constexpr T enc_prio() const {
		return T(prio);
	}
	template<B_t B> constexpr Encoded_Static<A0, B> enc_prio() const {
		return Encoded_Static<A0, B>(prio);
	}


	/* Is the task preemptable */
	const bool preemptable;

    /* Constant reference to the TCB */
    const arch::TCB & tcb;

	constexpr Task(id_t _id, prio_t _prio, bool preemptable, const arch::TCB &tcb)
	 	: id(_id), prio(_prio), preemptable(preemptable), tcb(tcb) {}
};

}; // namespace scheduler
}; // namespace os

#endif // __TASK_H__
