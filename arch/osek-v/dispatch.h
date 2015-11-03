#ifndef __OSEK_V_DISPATCHER_H__
#define __OSEK_V_DISPATCHER_H__

#include "os/scheduler/task.h"
#include "output.h"
#include "tcb.h"

namespace arch {
	static constexpr const int IDLESTACKSIZE = 4096;

struct Dispatcher {
#ifndef CONFIG_OS_SYSTEMCALLS_WIRED
    static const TCB* m_current;
	static TCB  m_idle;

	static noinline void idleEntry(void) {
		CALL_HOOK(PreIdleHook);
        while(true){
            Machine::sleep();
        }
	}

    static forceinline void doDispatch(const TCB *from, const TCB *to) {
        // update current context
        m_current = to;

		/* If we do not reset the idle loop, when leaving it the
		   PreIdleHook is not called correctly on the next dispatch
		   to idle */
		if (from == &m_idle && to != &m_idle) {
			m_idle.reset();
		}

		CALL_HOOK(PreTaskHook);

		if ((from == 0) || !from->is_running()) {
			to->start(from);
		} else {
			from->switchTo(to);
		}
	}


public:

	static forceinline void init(void) {
		m_idle.reset();
	}

	static forceinline void Idle(void) {
		doDispatch(m_current, &m_idle);
    }

	static forceinline void Prepare(const os::scheduler::Task& task) {
        task.tcb.reset();
	}


	static forceinline void Destroy(const os::scheduler::Task& task) {
        task.tcb.reset();
	}

	static forceinline void Dispatch(const os::scheduler::Task &next,
									 const os::scheduler::Task *current = 0) {
		const TCB *cur = current ? &current->tcb : m_current;
        if(cur == &next.tcb)  {
			return;
		}

        doDispatch(cur, &next.tcb);
	}

	static forceinline void ResumeToTask(const os::scheduler::Task &next,
										 const os::scheduler::Task *current = 0) {
		Dispatch(next, current);
	}

	static forceinline void StartToTask(const os::scheduler::Task next,
										const os::scheduler::Task *current = 0) {
		Dispatch(next, current);
	}

#else // os.systemcalls == wired
	static void ResumeToTask(const os::scheduler::Task &x) {};
#endif
};
}


#endif
