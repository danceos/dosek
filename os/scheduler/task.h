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
#include "util/encoded.h"
#include "util/inline.h"

namespace os {
namespace scheduler {

#define TASK(taskname) noinline void os::tasks::start_##taskname (void)

/** 
 * The basic task class 
 * */
class Task {
public:
	typedef uint8_t id_t;
	typedef uint8_t prio_t;
	typedef void (* const fptr_t)(void);

	const id_t id;
	template<typename T> constexpr T enc_id() const {
		return T(id);
	}
	template<B_t B> constexpr Encoded_Static<A0, B> enc_id() const {
		return Encoded_Static<A0, B>(id);
	}

	const prio_t prio;
	template<typename T> constexpr T enc_prio() const {
		return T(prio);
	}
	template<B_t B> constexpr Encoded_Static<A0, B> enc_prio() const {
		return Encoded_Static<A0, B>(prio);
	}

	fptr_t fun;

	constexpr Task(id_t _id, prio_t _prio, void (*f)(void)) : id(_id), prio(_prio), fun(f) {}
};

}; // namespace scheduler
}; // namespace os

#endif // __TASK_H__
