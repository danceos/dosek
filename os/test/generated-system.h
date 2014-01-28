// TODO: this file will be generated from the application configuration!

#include "os/scheduler/task.h"
#include "os/scheduler/tasklist.h"
#include "os/scheduler/scheduler.h"
#include "os/alarm.h"



#ifndef THETASKS
#define THETASKS

using os::scheduler::Task;

// task handlers
extern "C" __attribute__((weak_import)) void OSEKOS_TASK_Task1(void);
extern "C" __attribute__((weak_import)) void OSEKOS_TASK_Task2(void);
extern "C" __attribute__((weak_import)) void OSEKOS_TASK_Task3(void);
extern "C" __attribute__((weak_import)) void OSEKOS_TASK_Task4(void);

// task stacks
extern "C" uint8_t Task1_stack[];
extern "C" uint8_t Task2_stack[];
extern "C" uint8_t Task3_stack[];
extern "C" uint8_t Task4_stack[];

// task stack pointers
extern "C" void* stackptr_Task1;
extern "C" void* stackptr_Task2;
extern "C" void* stackptr_Task3;
extern "C" void* stackptr_Task4;

namespace os {
namespace tasks {

// the tasks
constexpr Task t1(1, 2, OSEKOS_TASK_Task1, &Task1_stack, stackptr_Task1, 4096);
constexpr Task t2(2, 3, OSEKOS_TASK_Task2, &Task2_stack, stackptr_Task2, 4096);
constexpr Task t3(3, 1, OSEKOS_TASK_Task3, &Task3_stack, stackptr_Task3, 4096);
constexpr Task t4(4, 4, OSEKOS_TASK_Task4, &Task4_stack, stackptr_Task4, 4096);

}; // namespace tasks
}; // namespace os

using namespace os::tasks;

// ****************************************************************
// TaskList Implementation
// ****************************************************************

namespace os { namespace scheduler {

/* Simpler array based task queue */
class TaskList : public TaskListStatic {

	// encoded task priorities
	Encoded_Static<A0, 17> task1;
	Encoded_Static<A0, 16> task2;
	Encoded_Static<A0, 15> task3;
	Encoded_Static<A0, 14> task4;

public:
	// idle task id/priority
	static constexpr auto idle_id = EC(13,0);
	static constexpr auto idle_prio = EC(12,0);

	TaskList() :
		TaskListStatic(),
		task1(0, 0),
		task2(0, 0),
		task3(0, 0),
		task4(0, 0) {}


	/** Set priority of task id to prio **/
	// returns an encoded 0 with the signature (B) of the modified task - prio.B
	template<typename T, typename S>
	forceinline value_coded_t set(const T id, const S prio) {
		//volatile value_coded_t signature;
		if(id == 1) {
			task1 = prio;
			return (task1 - prio).getCodedValue();
		} else if(id == 2) {
			task2 = prio;
			return (task2 - prio).getCodedValue();
		} else if(id == 3) {
			task3 = prio;
			return (task3 - prio).getCodedValue();
		} else if(id == 4) {
			task4 = prio;
			return (task4 - prio).getCodedValue();
		} else {
			assert(false);
			return 0;
		}
	}


	/** Get highest-priority task.
	  * Saves result ID in TaskList::id,
	  * and result priority in TaskList::prio.
	  * If no task is ready, TaskList::prio == TaskList::idle_prio
	  * and TaskList::id is undefined.
	  */
	template<typename T, typename S>
	forceinline value_coded_t head(T& id, S& prio) const {
		// initialize control flow signature
		static volatile value_coded_t signature;

		const value_coded_t signature0 = 10;
		signature = signature0;

		// start with idle id/priority
		id = idle_id;
		prio = idle_prio;

		// add initial signature
		id.vc += 10;
		prio.vc += 10;

		// task1 >= prio?
		signature += updateMax<10, 11>(prio, task1, id, EC(41, 1));
		const value_coded_t signature1 = signature0 + updateMax_signature(11, prio, task1);
		assert((signature - signature1) % S::A == 0);

		// task2 >= prio?
		signature += updateMax<11, 12>(prio, task2, id, EC(42, 2));
		const value_coded_t signature2 = signature1 + updateMax_signature(12, prio, task2);
		assert((signature - signature2) % S::A == 0);

		// task3 >= prio?
		signature += updateMax<12, 13>(prio, task3, id, EC(43, 3));
		const value_coded_t signature3 = signature2 + updateMax_signature(13, prio, task3);
		assert((signature - signature3) % S::A == 0);

		// task4 >= prio?
		signature += updateMax<13, 14>(prio, task4, id, EC(44, 4));
		const value_coded_t signature4 = signature3 + updateMax_signature(14, prio, task4);
		assert((signature - signature4) % S::A == 0);

		// restore idle_id if idle_id >= prio
		signature += updateMax<14, 15>(prio, idle_prio, id, idle_id);
		const value_coded_t signature5 = signature4 + updateMax_signature(15, prio, idle_prio);
		assert((signature - signature5) % S::A == 0);

		// subtract last signature
		id.vc -= 15;
		prio.vc -= 15;

		// check signatures
		assert(id.check());
		assert(prio.check());

		return signature;
	}


	template<typename T, typename S>
	forceinline value_coded_t insert(const T& id, const S& prio) {
		// if(DEBUG) kout << "+++ Task " << id.decode() << " with priority " << prio.decode() << " is ready" << endl;

		return set(id, prio);
	}

	template<typename T>
	forceinline value_coded_t remove(const T& id) {
		// if(DEBUG) kout << "--- Task " << id.decode() << " removed from task queue" << endl;

		return set(id, EC(5, 0));
	}

	template<typename T, typename S>
	forceinline value_coded_t promote(const T& id, const S& newprio) {
		// if(DEBUG) kout << "^^^ Promoting task " << id.decode() << " to priority " << newprio.decode() << endl;

		return set(id, newprio);
	}

	template<typename T, typename S>
	forceinline value_coded_t dequeue(T& id, S& prio) {
		static value_coded_t sig1;

		sig1 = head(id, prio);

		value_coded_t sig2;
		if(prio != idle_prio) {
			sig2 = remove(id);
			// IDEA: set id.vc += sig2 + X; ?
		} else {
			// IDEA: set id.vc = sig2 + X; ?
			sig2 = 42;
		}

		// TODO: more control flow checks?

		return sig1+sig2;
	}


	// DEBUGGING
	void print() const {
		//kout << "(" << task1.decode() << "), ";
		//kout << "(" << task2.decode() << "), ";
		//kout << "(" << task3.decode() << "), ";
		//kout << "(" << task4.decode() << ")" << endl;
	}
};

class Scheduler : public SchedulerStatic {
protected:
	os::scheduler::TaskList tlist;
public:
	Scheduler() : SchedulerStatic() {}

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

	forceinline void Schedule_impl(void) {
		if(in_syscall()) {
			// in syscall: reschedule directly
			Reschedule();
		} else {
			// not in syscall (probably in ISR): request reschedule AST
			request_reschedule_ast();
		}
	}

	forceinline void ActivateTask_impl(const Task t) {
		ActivateTask_impl(t.enc_id<3>());
	}

	template<typename T>
	forceinline void ActivateTask_impl(const T id) {
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

		Schedule_impl();
	}

	forceinline void TerminateTask_impl() {
		tlist.remove(current_task);
		Schedule_impl();
	}

	forceinline void ChainTask_impl(const Task t) {
		ChainTask_impl(t.enc_id<3>());
	}

	template<typename T>
	forceinline void ChainTask_impl(const T id) {
		tlist.remove(current_task);
		ActivateTask_impl(id);
	}
};

extern Scheduler scheduler;

// TODO: more meaningful names
// currently the "normal" name is a syscall wrapper for
// the actual syscall which has ...C suffix

template<typename T>
noinline void ActivateTaskC_impl(const T id) {
	scheduler.ActivateTask_impl(id);
}

/**
 * @satisfies{13,2,3,1}
 */
forceinline void ActivateTask_impl(const Task& t) {
	auto id = t.enc_id<3>();

	syscall(ActivateTaskC_impl<decltype(id)>, id);
}

template<typename T>
noinline void ChainTaskC_impl(const T id) {
	scheduler.ChainTask_impl(id);
}

/**
 * @satisfies{13,2,3,3}
 */
forceinline void ChainTask_impl(const Task& t) {
	auto id = t.enc_id<3>();

	syscall(ChainTaskC_impl<decltype(id)>, id);

	Machine::unreachable();
}

noinline void TerminateTaskC_impl(uint32_t dummy);

/**
 * @satisfies{13,2,3,2}
 */
forceinline void TerminateTask_impl() {
	syscall(TerminateTaskC_impl);

	Machine::unreachable();
}

noinline void ScheduleC_impl(uint32_t dummy);

/**
 * @satisfies{13,2,3,4}
 */
forceinline void Schedule_impl() {
	syscall(ScheduleC_impl);
}

}; // namespace scheduler
}; // namespace os

namespace os {

class Alarm;
extern Alarm alarm0;

class Alarm : public AlarmStatic {
	/** \brief task to activate */
	const Task* const task_;
public:
	constexpr Alarm(Counter& counter) : AlarmStatic(counter), task_(0) {}
	constexpr Alarm(Counter& counter, const Task& task) : AlarmStatic(counter), task_(&task) {}


	static forceinline void checkCounter(Counter& counter) {
		// TODO: call all generated alarms
		if (alarm0.checkTrigger(&counter)) {
			if(alarm0.task_) {
                #if DEBUG
				serial << "Alarm trigger" << endl;
                #endif

				os::scheduler::scheduler.ActivateTask_impl(*alarm0.task_);
			}
		}
	}
};


}


#endif
