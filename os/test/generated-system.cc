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

EncodedCounter<99> counter0;
__attribute__((weak)) EncodedAlarm<77, 99> alarm0(counter0);


void inlinehint Counter::tick() {
	counter0.do_tick();

	Alarm::checkCounter(counter0);
}

void inlinehint Alarm::checkCounter(const Counter &counter) {
	if ((&counter == &counter0) && alarm0.checkTrigger()) {
	}
}

}; // os


void __OS_HOOK_PreIdleHook() {}

