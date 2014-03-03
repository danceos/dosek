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

extern "C" void __OS_ASTSchedule (int dummy);

#endif // __SCHEDULER_H__
