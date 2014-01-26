/**
 * @file

 * @brief Scheduler implementation
 */
#ifndef __SCHEDULER_H__
#define __SCHEDULER_H__

#include "util/assert.h"
#include "scheduler/tasklist.h"
#include "syscall.h"
#include "dispatch.h"
#include "reschedule-ast.h"
#include "thetasks.h"

using namespace arch;

namespace os { namespace scheduler {

class Scheduler {
protected:
	Encoded_Static<A0, 2> current_prio;
	Encoded_Static<A0, 3> current_task;
	os::scheduler::TaskList tlist;

public:
	Scheduler() : current_prio(0), current_task(0) {}

	forceinline void Reschedule(void) {
		// TODO: control flow check

		// set current (=next) task from task list
		tlist.head(current_task, current_prio);

		// dispatch or enter idle
		if(current_task == t1.enc_id<1>()) {
			Dispatcher::Dispatch(t1);
		} else if(current_task == t2.enc_id<1>()) {
			Dispatcher::Dispatch(t2);
		} else if(current_task == t3.enc_id<1>()) {
			Dispatcher::Dispatch(t3);
		} else if(current_task == t4.enc_id<1>()) {
			Dispatcher::Dispatch(t4);
		} else if(current_task == TaskList::idle_id) {
			Dispatcher::idle();
		} else {
			assert(false);
		}
	}

	forceinline void Schedule(void) {
		if(in_syscall()) {
			// in syscall: reschedule directly
			Reschedule();
		} else {
			// not in syscall (probably in ISR): request reschedule AST
			request_reschedule_ast();
		}
	}

	forceinline void ActivateTask(const Task t) {
		ActivateTask(t.enc_id<3>());
	}

	template<typename T>
	forceinline void ActivateTask(const T id) {
		if(id == t1.enc_id<1>()) {
			t1.reset_sp();
			value_coded_t sig = tlist.insert(t1.enc_id<3>(),  t1.enc_prio<4>());
			assert(sig == 13);
		} else if(id == t2.enc_id<1>()) {
			t2.reset_sp();
			value_coded_t sig = tlist.insert(t2.enc_id<3>(),  t2.enc_prio<4>());
			assert(sig == 12);
		} else if(id == t3.enc_id<1>()) {
			t3.reset_sp();
			value_coded_t sig = tlist.insert(t3.enc_id<3>(),  t3.enc_prio<4>());
			assert(sig == 11);
		} else if(id == t4.enc_id<1>()) {
			t4.reset_sp();
			value_coded_t sig = tlist.insert(t4.enc_id<3>(),  t4.enc_prio<4>());
			assert(sig == 10);
		} else {
			assert(false);
		}

		Schedule();
	}

	forceinline void TerminateTask() {
		tlist.remove(current_task);
		Schedule();
	}

	forceinline void ChainTask(const Task t) {
		ChainTask(t.enc_id<3>());
	}

	template<typename T>
	forceinline void ChainTask(const T id) {
		tlist.remove(current_task);
		ActivateTask(id);
	}
};

extern Scheduler scheduler;

// TODO: more meaningful names
// currently the "normal" name is a syscall wrapper for
// the actual syscall which has ...C suffix

template<typename T>
noinline void ActivateTaskC(const T id) {
	scheduler.ActivateTask(id);
}

/**
 * @satisfies{13,2,3,1}
 */
forceinline void ActivateTask(const Task& t) {
	auto id = t.enc_id<3>();

	syscall(ActivateTaskC<decltype(id)>, id);
}

template<typename T>
noinline void ChainTaskC(const T id) {
	scheduler.ChainTask(id);
}

/**
 * @satisfies{13,2,3,3}
 */
forceinline void ChainTask(const Task& t) {
	auto id = t.enc_id<3>();

	syscall(ChainTaskC<decltype(id)>, id);

	Machine::unreachable();
}

noinline void TerminateTaskC(uint32_t dummy);

/**
 * @satisfies{13,2,3,2}
 */
forceinline void TerminateTask() {
	syscall(TerminateTaskC);

	Machine::unreachable();
}

noinline void ScheduleC(uint32_t dummy);

/**
 * @satisfies{13,2,3,4}
 */
forceinline void Schedule() {
	syscall(ScheduleC);
}

}};

#endif // __SCHEDULER_H__
