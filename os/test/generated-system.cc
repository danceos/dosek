#include "generated-system.h"

/**
 * @file
 * @ingroup scheduler
 * @brief Object instantiation
 */

// task stacks

namespace os {
namespace scheduler {

noinline void TerminateTaskC_impl(__attribute__ ((unused)) uint32_t dummy) {
}

noinline extern "C" void __OS_ASTSchedule(__attribute__ ((unused)) int dummy) 
{
}

}; // scheduler
}; // os


namespace os {

Counter counter0;
__attribute__((weak)) Alarm alarm0(counter0);


void inlinehint Counter::tick() {
	if(counter0.value == counter0.maxallowedvalue) {
		counter0.value = 0;
	} else {
		counter0.value++;
	}

	Alarm::checkCounter(counter0);
}

void inlinehint Alarm::checkCounter(const Counter &counter) {
	if ((&counter == &counter0) && alarm0.checkTrigger(&counter)) {
	}
}

}; // os


void __OS_HOOK_PreIdleHook() {}

