#ifndef __DOSEK_OS_FSM_SIMPLE
#define __DOSEK_OS_FSM_SIMPLE

#include "os/scheduler/task.h"
#include "dispatch.h"
#include "os/util/assert.h"



namespace os {
namespace fsm {


class SimpleFSM {
 public:
	typedef os::scheduler::Task::id_t task_t;
	typedef unsigned int internal_state_t;

	struct Transition {
		internal_state_t source;
		internal_state_t target;
		task_t next_task;

		constexpr Transition(internal_state_t source, internal_state_t target, task_t next_task)
		  : source(source), target(target), next_task(next_task) {};
	};

	SimpleFSM(internal_state_t initial_state) : state(initial_state) {};

	void set_state(internal_state_t state) { this->state = state; }
	internal_state_t get_state() const { return state; }

	task_t event(const Transition * transition_table, unsigned transition_length) {
		// kout << "old state: " << state << endl;
		for (unsigned i = 0; i < transition_length; i++) {
			if (transition_table[i].source == state) {
				state = transition_table[i].target;
				// kout << "new_state " << state << endl;
				return transition_table[i].next_task;
			}
		}
		kout << "Really bad" << endl;
		assert(false);
		return -1;
	}

private:
	internal_state_t state;
};

}
}

#endif
