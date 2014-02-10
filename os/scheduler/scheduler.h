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

namespace os { namespace scheduler {

extern void ScheduleC_impl(uint32_t dummy);

}};

#endif // __SCHEDULER_H__
