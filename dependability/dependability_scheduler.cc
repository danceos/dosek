
#include "dependability_service.h"

namespace dep {
	Dependability_Scheduler::Dependability_Scheduler() : current(0)
	{}

	unsigned Dependability_Scheduler::get_next()
	{
		current = (current + 1) % OS_all_CheckedObjects_size;
		return current;
	}

	void Dependability_Scheduler::update(unsigned int index,
	                                     Dependability_Scheduler::Object_State state)
	{
		(void) index;
		(void) state;
	}
}
