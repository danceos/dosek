
#include "dependability_service.h"

namespace dep {
	Dependability_Scheduler::Dependability_Scheduler() : current(1)
	{}

	unsigned int Dependability_Scheduler::get_next()
	{
		++current;
		unsigned int diff_max = 0, index_max = 0;
		for (unsigned int i = 0; i < OS_all_CheckedObjects_size; ++i) {
			unsigned int diff = current - OS_all_CheckedObjects[i].weight;
			if (diff_max < diff && !OS_all_CheckedObjects[i].counter) {
				diff_max = diff;
				index_max = i;
			}
		}
		return index_max;
	}

	void Dependability_Scheduler::update(unsigned int index,
	                                     Dependability_Scheduler::Object_State state)
	{
		if (state == SUCCESS) {
			OS_all_CheckedObjects[index].weight = current;
		}
	}

#if 0
	/* This is an alternative scheduler that determines the next object
	 * to check via round robin. Note: current has a different semantic,
	 * but this is just an implementation detail. */
	Dependability_Scheduler::Dependability_Scheduler() : current(0)
	{}

	unsigned int Dependability_Scheduler::get_next()
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
#endif
}
