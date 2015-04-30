/**
 * @file
 * @ingroup posix
 * @brief Posix task dispatching
 */

#ifndef __DISPATCH_H__
#define __DISPATCH_H__

#include "os/util/inline.h"
#include "os/scheduler/task.h"

#include "signalinfo.h"
#include "output.h"
#include "tcb.h"
#include "os/hooks.h"

namespace arch {

static const int IDLESTACKSIZE = 4096;

class Dispatcher {
    static const TCB* m_current;
	static TCB  m_idle;

	static noinline void idleEntry(void) {
        debug << "idleEntry" << endl;
        //int i = 0;
		CALL_HOOK(PreIdleHook);
        while(true){
            //debug << "Idle: " << i++ <<endl;
            Machine::nop();
            // Machine::enable_interrupts(); // idle context should have unmask signals anyway
            // Machine::halt();
        }
	}

    static forceinline void doDispatch(const TCB *from, const TCB *to) {
        // update current context
        m_current = to;

		/* If we do not reset the idle loop, when leaving it the
		   PreIdleHook is not called correctly on the next dispatch
		   to idle */
		if (from == &m_idle) {
			m_idle.reset();
		}

		CALL_HOOK(PreTaskHook);

		if (to->basic_task) {
			to->switch_to_basic_task(from);
		} else {
			if ((from == 0) || !from->is_running()) {
				to->start(from);
			} else {
				from->switchTo(to);
			}
		}
    }

public:

    static void init(void) {
        // setup idle context
		m_idle.reset();
    }


	static forceinline void idle(void) {
       debug << "Enter idle" << endl;
       doDispatch(m_current, &m_idle);
    }

	static forceinline void Destroy(const os::scheduler::Task& task) {
        task.tcb.reset();
	}

	static forceinline void Dispatch(const os::scheduler::Task &next,
									 const os::scheduler::Task *current = 0) {
        // Do not resume yourself...
		// kout << (void*)current << " " << (void*) &next << endl;
		const TCB *cur = current ? &current->tcb : m_current;
        if(cur == &next.tcb)  {
			debug << "Dispatch to ID " << (int)next.id << " via return" << endl;
			return;
		}

        debug << "Dispatch to ID: " << (int)next.id << " " << ((void *)&next.tcb) << endl;

        doDispatch(cur, &next.tcb);
	}

	static forceinline void ResumeToTask(const os::scheduler::Task &next,
										 const os::scheduler::Task *current = 0) {
		//assume(next.tcb.is_running());
		Dispatch(next, current);
	}

	static forceinline void StartToTask(const os::scheduler::Task next,
										const os::scheduler::Task *current = 0) {
		//assume(!next.tcb.is_running());
		Dispatch(next, current);
	}

};

} // namespace arch


#endif // __DISPATCH_H__
