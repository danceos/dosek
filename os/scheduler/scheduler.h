/**
 * @file

 * @brief Scheduler implementation
 */
#ifndef __SCHEDULER_H__
#define __SCHEDULER_H__

#include "util/assert.h"
#include "scheduler/tasklist.h"
#include "syscall.h"
#include "dispatch.h"
#include "reschedule-ast.h"


using namespace arch;

namespace os { namespace scheduler {

extern void ScheduleC_impl(uint32_t dummy);

class SchedulerStatic {
protected:
	Encoded_Static<A0, 2> current_prio;
	Encoded_Static<A0, 3> current_task;

public:
	SchedulerStatic() : current_prio(0), current_task(0) {}
};

}};

#endif // __SCHEDULER_H__
