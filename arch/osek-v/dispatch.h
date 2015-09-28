#ifndef __OSEK_V_DISPATCHER_H__
#define __OSEK_V_DISPATCHER_H__

#include "os/scheduler/task.h"

namespace arch {
struct Dispatcher {
	static void ResumeToTask(const os::scheduler::Task &x) {};
};
}

#endif
