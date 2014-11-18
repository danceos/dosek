#define GIC_DIST_BASE (0xF8F01000)
#define GIC_CPU_BASE  (0xF8F00100)

#define SERIAL_BASE 0xE0001000

#define PRIVATE_TIMER_BASE 0xF8F00600
#define WDT_TIMER_BASE     0xF8F00620
#define CPU_FREQ_HZ 666666687


// According to GICdist().ICTR = 2
// max IRQs = 32*(ICTR+1)
#define cfIRQ_MAXHANDLERNUM 96

/**
 * @name IRQ priot, lower number is higher priority
 * @{
 */
#define IRQ_PRIO_LOWEST      0xff //!< the lowest available priority
#define IRQ_PRIO_RESCHEDULE    0xe0   //!< reschedule (AST) software interrupt
#define IRQ_PRIO_DISPATCH 0x10 //!< dispatch IRQ priority prio
#define IRQ_PRIO_LOCAL_TIMER 0x30 //!< local CPU timer interrupt
#define IRQ_PRIO_SYSCALL 0x20 //!< syscall software interrupt
#define IRQ_PRIO_MIN_ISR2 0x30 //!< syscall software interrupt

/**@}*/



