#include "generated-system.h"

/**
 * @file
 * @ingroup scheduler
 * @brief Object instantiation
 */

// task stacks
uint8_t Task1_stack[4096];
uint8_t Task2_stack[4096];
uint8_t Task3_stack[4096];
uint8_t Task4_stack[4096];

void* stackptr_Task1 = 0;
void* stackptr_Task2 = 0;
void* stackptr_Task3 = 0;
void* stackptr_Task4 = 0;

namespace os {
namespace scheduler {

Scheduler scheduler;

noinline void TerminateTaskC_impl(__attribute__ ((unused)) uint32_t dummy) {
	scheduler.TerminateTask_impl();
}

noinline void ScheduleC_impl(__attribute__ ((unused)) uint32_t dummy) {
	scheduler.Reschedule();
}

}; // scheduler
}; // os


namespace os {

__attribute__((weak)) Alarm alarm0(counter0);

void Alarm_checkCounter(Counter &counter) {
	Alarm::checkCounter(counter);
}
constexpr Encoded_Static<A0, 13> TaskList::idle_id;
constexpr Encoded_Static<A0, 12> TaskList::idle_prio;


}; // os

void __OS_HOOK_PreIdleHook() {}
