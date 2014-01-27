/**
 * @file
 * @ingroup scheduler
 * @brief Object instantiation
 */

#include "thetasks.h"
#include "scheduler.h"

namespace os {
namespace scheduler {

Scheduler scheduler;

noinline void TerminateTaskC_impl(__attribute__ ((unused)) uint32_t dummy) {
	scheduler.TerminateTask();
}

noinline void ScheduleC_impl(__attribute__ ((unused)) uint32_t dummy) {
	scheduler.Reschedule();
}

};
};
