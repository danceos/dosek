#include "syscall.h"
#include "dispatch.h"
#include "gic.h"
#include "machine.h"
#include "util/assert.h"
#include "os/scheduler/scheduler.h"

extern "C" uint8_t _estack_os;

namespace arch {

IRQ_HANDLER(IRQ_RESCHEDULE) {
    // block ISR2s by raising GIC task priority
    GIC::set_task_prio(IRQ_PRIO_SYSCALL);

    // change to OS page directory
    //PageDirectory::enable(pagedir_os);

    // reset save_sp to detect IRQ from non-userspace in idt.S
    save_sp = 0;

    // send end-of-interrupt signal
    GIC::send_eoi(irq);

    // set user SP
    Machine::switch_mode(Machine::SYSTEM);
    asm volatile("mov sp, %0" :: "r"(&_estack_os - 2048));
    Machine::switch_mode(Machine::SUPERVISOR);

    asm volatile("mov lr, %0" :: "r"((uint32_t)__OS_ASTSchedule));
    asm volatile("subs pc, lr, #0");

    Machine::unreachable();
}

}; // namespace arch
