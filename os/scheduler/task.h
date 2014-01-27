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

namespace os {
namespace scheduler {

/**
 * The basic task class
 * */
class Task {
public:
	typedef uint8_t id_t;
	typedef uint8_t prio_t;
	typedef void (* const fptr_t)(void);

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

	// task function
	fptr_t fun;

	// task stack
	void * const stack;

	// reference to saved stack pointer
	// TODO: encode?
	void* &sp;

	const int stacksize;

	inline void reset_sp(void) const {
		sp = (uint8_t*)stack + stacksize - 16;
	}

	inline bool is_running(void) const {
		return sp != (uint8_t*)stack + stacksize - 16;
	}

	constexpr Task(id_t _id, prio_t _prio, fptr_t f, void *s, void* &sptr, int stacksize)
	 	: id(_id), prio(_prio), fun(f), stack(s), sp(sptr), stacksize(stacksize) {}
};

}; // namespace scheduler
}; // namespace os

#endif // __TASK_H__
