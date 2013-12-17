/**
 * @file
 * @brief
 *
 */
#include "util/assert.h"
#include "scheduler/tasklist.h"

namespace os { namespace scheduler {

class Scheduler {
protected:
	Encoded_Static<A0, 2> current_prio;
	Encoded_Static<A0, 3> current_task;
	os::scheduler::TaskList tlist;

public:
	Scheduler() : current_prio(0), current_task(0) {}

	forceinline void dispatch(void) {
		// TODO: use functionwrapper for return address save and "branch" check
		if(current_task == t1.enc_id<1>()) {
			t1.fun();
		} else if(current_task == t2.enc_id<1>()) {
			t2.fun();
		} else if(current_task == t3.enc_id<1>()) {
			t3.fun();
		} else if(current_task == t4.enc_id<1>()) {
			t4.fun();
		} else {
			assert(false);
		}
	}

	forceinline void Schedule(void) {
		// TODO: store at static addr?
		Encoded_Static<A0, 1> old_task;
		old_task = current_task;
		Encoded_Static<A0, 2> old_prio;
		old_prio = current_prio;

		// TODO: encode everything!
		while(true) {
			if(old_task != 0) tlist.insert(old_task, old_prio);

			tlist.dequeue(current_task, current_prio);

			if(old_task == current_task) break;

			dispatch();
		}
	}

	forceinline void ActivateTask(const Task t) {
		ActivateTask(t.enc_id<3>());
	}

	template<typename T>
	forceinline void ActivateTask(const T id) {
		if(id == t1.enc_id<1>()) {
			value_coded_t sig = tlist.insert(t1.enc_id<3>(),  t1.enc_prio<4>());
			assert(sig == 13);
		} else if(id == t2.enc_id<1>()) {
			value_coded_t sig = tlist.insert(t2.enc_id<3>(),  t2.enc_prio<4>());
			assert(sig == 12);
		} else if(id == t3.enc_id<1>()) {
			value_coded_t sig = tlist.insert(t3.enc_id<3>(),  t3.enc_prio<4>());
			assert(sig == 11);
		} else if(id == t4.enc_id<1>()) {
			value_coded_t sig = tlist.insert(t4.enc_id<3>(),  t4.enc_prio<4>());
			assert(sig == 10);
		} else {
			assert(false);
		}

		Schedule();
	}

	forceinline void TerminateTask() {
		// currently (single stack non-preemptive BCC1), this is a noop before return
	}

	forceinline void ChainTask(const Task t) {
		ChainTask(t.enc_id<3>());
	}

	template<typename T>
	forceinline void ChainTask(const T id) {
		// currently (single stack non-preemptive BCC1), this is very simple:
		TerminateTask();
		ActivateTask(id);
	}
};

extern Scheduler scheduler;

/**
 * @satisfies{13,2,3,1}
 */
forceinline void ActivateTask(const Task t) {
	scheduler.ActivateTask(t.enc_id<3>());
}

/**
 * @satisfies{13,2,3,3}
 */
forceinline void ChainTask(const Task t) {
	scheduler.ChainTask(t.enc_id<3>());
}

/**
 * @satisfies{13,2,3,2}
 */
forceinline void TerminateTask() {
	scheduler.TerminateTask();
}

}};
