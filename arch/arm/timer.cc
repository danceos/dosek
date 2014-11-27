/**
 * @file
 * @ingroup arm
 * @brief ARM Private Timer
 */

#include "timer.h"
#include "gic.h"
#include "os/counter.h"

namespace arch {

volatile Timer::PRV_Timer_regs * const Timer::timer = reinterpret_cast<volatile Timer::PRV_Timer_regs * const>(PRIVATE_TIMER_BASE);

void Timer::init() {
    GIC::set_irq_priority(IRQ_LOCAL_TIMER, IRQ_PRIO_LOCAL_TIMER);
    GIC::enable_irq(IRQ_LOCAL_TIMER);

    set_periodic(1); // TODO find correct interval
}

void Timer::set_periodic(uint16_t rate_in_ms) {
    // Calculate Reload value
    const uint32_t TIMER_FREQ_IN_kHZ = (CPU_FREQ_HZ / 2) / 1000;

    timer->load = rate_in_ms * TIMER_FREQ_IN_kHZ;

    timer->control = 0; // Clear control register
    timer->control = (1<<2) | (1 << 1) | (1 << 0); // Enable ISR, Auto reload, enable
}

extern "C" void* irq_handler_29(void* task_sp, uint32_t irq) {
	(void)irq;
    Timer::ack_isr(); // acknowledge timer IRQ

    GIC::set_task_prio(IRQ_PRIO_LOWEST); // TODO: enable ISR2, in_syscall -> false
	os::Counter::tick();

    return task_sp;
}

}; // namespace arch
