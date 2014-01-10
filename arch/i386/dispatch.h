/**
 * @file
 * @ingroup i386
 * @brief i386 task dispatching
 */

#ifndef __DISPATCH_H__
#define __DISPATCH_H__

#include "os/util/inline.h"
#include "os/scheduler/task.h"
#include "idt.h"
#include "lapic.h"

namespace os {
// TODO: remove pointer usage by determining static location from task ID
/** \brief Stack pointer save location */
extern void** save_sp;
}
using os::save_sp;

namespace arch {

class Dispatcher {
public:
	static forceinline void dispatch_syscall(const uint32_t& pagedir, const uint32_t& stackptr, const uint32_t& ip) {
		asm volatile("int %0" :: "i"(IRQ_DISPATCH), "d"(pagedir), "b"(stackptr), "c"(ip));
	}

	static forceinline void Dispatch(const os::scheduler::Task& task) {
		// TODO: remove pointer usage
		save_sp = &task.sp;

		// TODO: control flow check
		if(task.is_running()) {
			// not resuming, pass task function
			dispatch_syscall((uint32_t) task.id, (uint32_t)task.sp, (uint32_t)task.fun);
		} else {
			// resuming, pass stackpointer with saved IP
			dispatch_syscall((uint32_t) task.id, (uint32_t)task.sp, (uint32_t)&task.sp);
		}
	}

	static forceinline void Idle(void) {
		// TODO: real idle loop
		asm("int3");
		asm("hlt");

		// should never come here
		asm("int3");

		while(true) {
			asm("nop");
		}
	}
};

} // namespace arch

#endif // __DISPATCH_H__