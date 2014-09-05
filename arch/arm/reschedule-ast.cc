#include "syscall.h"
#include "dispatch.h"
#include "irq.h"
#include "machine.h"
#include "util/assert.h"
#include "os/scheduler/scheduler.h"

extern "C" uint8_t _estack_os;

namespace arch {

static const uint32_t reschedule_return[]  = {
    (uint32_t) &(_estack_os) - 2048,
    (uint32_t) __OS_ASTSchedule,
};

#if 0
IRQ_HANDLER(IRQ_RESCHEDULE) {
    // block ISR2s by raising GIC task priority
    GIC::set_task_prio(128);

    // change to OS page directory
    //PageDirectory::enable(pagedir_os);

    // reset save_sp to detect IRQ from non-userspace in idt.S
    save_sp = 0;

    // send end-of-interrupt signal
    GIC::send_eoi(IRQ_RESCHEDULE); // TODO use ID from accept

    // return from interrupt and proceed with syscall in ring 3
    //asm volatile("ldr sp, %0" :: "i"(&iret_schedule));
    //Machine::return_from_interrupt();
    asm volatile("ldr sp, %0; LDM sp!, {sp,pc}^" :: "i"(&reschedule_return));
    Machine::unreachable();
}
#endif

}; // namespace arch
