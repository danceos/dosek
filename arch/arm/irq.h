/**
 * @file
 * @ingroup i386
 * @brief i386 Interrupt structures
 */

#ifndef IDT_H_
#define IDT_H_

#include "stdint.h"
#include "util/inline.h"
#include "machine.h"
#include "platform.h"

namespace arch {

typedef uint16_t irq_id; //!< 10 bit interrupt ID
typedef uint8_t priority; //!< 8 bit interrupt priority

/** \brief Generic Interrupt Controller */
class GIC {
public:
    enum gic_reg {
        GICD_BASE = GIC_DIST_BASE,      //!< base address for GIC distributor
        GICD_CTRL = GICD_BASE + 0x0,    //!< distributor control register
        GICD_IPR  = GICD_BASE + 0x400,    //!< distributor control register
        GICD_SGIR = GICD_BASE + 0xF00,  //!< software generated interrupt register

        GICC_BASE = GIC_CPU_BASE,       //!< base address for CPU interface
        GICC_PMR  = GICC_BASE + 0x4,    //!< interrupt priority mask register
        GICC_CTRL = GICC_BASE + 0x0,    //!< CPU interface control register
        GICC_IAR  = GICC_BASE + 0xC,    //!< interrupt acknowledge register
        GICC_EOIR = GICC_BASE + 0x10,   //!< end-of-interrupt register
        GICC_RPR  = GICC_BASE + 0x14,   //!< running priority register
    };

private:

    static forceinline void write_reg(gic_reg reg, uint32_t val) {
        *((volatile uint32_t*) reg) = val;
    }

    static forceinline uint32_t read_reg(gic_reg reg) {
        return *((volatile uint32_t*) reg);
    }

public:
    /** \brief Initialize and enable the GIC */
    static void init();

    /** \brief Enable the GIC (distributor and CPU interface) */
    static forceinline void enable() {
        write_reg(GICD_CTRL, 1); // enable the distributor

        // enable the CPU interface:
        // enable IRQs [0], FIRQs [1], and map Group1 to FIRQs [3]
        write_reg(GICC_CTRL, (1<<3) | (1<<1) | (1<<0));
    }

    /** \brief Accept interrupt and get interrupt ID */
    static forceinline irq_id accept() {
        // accept the interrupt and read its ID
        irq_id id = read_reg(GICC_IAR) & 0xFFF;

        //if(id & 0x1FF == 1023) spurious_interrupt();

        return id;
    }

    /** \brief Send end-of-interrupt signal */
    static forceinline void send_eoi(irq_id id) {
        write_reg(GICC_EOIR, id);
    }

    /** \brief Set interrupt priority (0: highest) */
    static forceinline void set_irq_priority(irq_id id, priority prio) {
        // thankfully, 8 bit accesses are possible for this
        *((volatile uint8_t*) (GICD_IPR + id)) = prio;
    }

    /** \brief Trigger SGI (software-generated interrupt) */
    static forceinline void trigger(uint8_t irq) {
        //pseudo_static_assert(irq < 0xFF, "Software-generated interrupt numbers are only 0-15");

        // write software generated irq register
        // distribute to this CPU
        write_reg(GICD_SGIR, (irq & 0xFF) | (2 << 23));
    }

    /** \brief Set task priority
     *
     * This will block all IRQs higher than the given priority.
     */
    static forceinline void set_task_prio(uint8_t prio) {
        write_reg(GICC_PMR, prio);
    }

    /** \brief Return task priority */
    static forceinline uint8_t get_task_prio() {
        return static_cast<uint8_t>(read_reg(GICC_PMR));
    }

    /** \brief Return processor interrupt priority */
    static forceinline uint8_t get_processor_prio() {
        return static_cast<uint8_t>(read_reg(GICC_RPR) & 0xFF);
    }
};


/**
 * @name IRQ numbers
 * @{
 */
#define IRQ_SYSCALL 2 //!< syscall software interrupt
#define IRQ_RESCHEDULE 1 //!< reschedule (AST) software interrupt
#define IRQ_DISPATCH 0 //!< dispatcher (AST) software interrupt
#define IRQ_LOCAL_TIMER 29 //!< local CPU timer interrupt
#define IRQ_WDT 30 //!< local watchdog timer interrupt
/**@}*/


/**
 * @name IRQ handler macros
 *
 * To define an interrupt handler after the context has been saved use the
 * ISR macro (this could be used for application ISR1s).
 * To define an interrupt handler without context saving or stack
 * adjustments use the IRQ_HANDLER macro. Take care to save and restore
 * registers and stack before usage!
 * @{
 */

/** \brief Define a free-standing interrupt handler
 *
 * This code will be jumped to directly when the interrupt occurs.
 * No context saving or stack adjustment is performed!
 * To finish interrupt handling call Machine::return_from_interrupt() !
 *
 * \param irqno IRQ number
 */
#define IRQ_HANDLER(irqno) IRQ_HNDLR(irqno)

/** \brief Define a free-standing interrupt handler
 *
 * This helper macro is needed to allow macro expansion for the argument
 * of the IRQ_HANDLER macro.
 * \see IRQ_HANDLER
 *
 * \internal
 */
#define IRQ_HNDLR(irqno) \
	extern "C" __attribute__((naked)) void irq_handler_ ## irqno (uint32_t return_address, uint32_t irq)


/** \brief Attach interrupt handler function to interrupt
 *
 * This macro defines the actual interrupt handler which will be jumped
 * to after the context is saved and stack changed. To simulate a function call
 * of the handler function the context pointer from %esi is passed to the
 * *inlined* handler function. After the inlined code a jump to the common
 * exit code is performed.
 * \see ISR
 *
 * \param irqno IRQ number
 * \param handler Interrupt handler function, *must be forceinline*
 * \hideinitializer
 */
#define ISR_HANDLER(irqno, handler) \
	extern "C" void isr_ ## irqno (void) { \
		struct task_context* task; \
		struct cpu_context* cpu; \
		uint32_t checksum; \
		uint32_t pagedir; \
		asm volatile("" : "=S"(cpu), "=b"(task), "=c"(checksum), "=D"(pagedir)); \
		handler(cpu, task); \
		asm volatile("jmp handler_exit" :: "S"(cpu), "b"(task), "c"(checksum), "D"(pagedir)); \
		Machine::unreachable(); \
	}

/** \brief Define an interrupt handler
 *
 * This code will be jumped to after the context is saved to the stack
 * and then executed on interrupt/kernel stack.
 *
 * \param irqno IRQ number
 * \hideinitializer
 */
#define ISR(irqno) \
	forceinline void irq_handler_fun_ ## irqno (struct cpu_context* cpu, struct task_context* task); \
	ISR_HANDLER(irqno, irq_handler_fun_ ## irqno); \
	forceinline void irq_handler_fun_ ## irqno (__attribute__((unused)) struct cpu_context* cpu, __attribute__((unused)) struct task_context* task)
/**@}*/

#if 0


/** \brief Context saved by CPU on interrupt/trap/syscall */
struct cpu_context {
	uint32_t eip; //!< source address
	uint32_t cs; //!< source code segment selector

	uint32_t eflags; //!< original flags

	// only pushed when coming from ring>0:
	uint32_t user_esp; //!< userspace stack pointer
	uint32_t ss; //!< userspace stack segment selector
} __attribute__((packed));

/** \brief Application (task) context (saved by IRQ handlers) */
struct task_context {
	// esp is not valid, TODO: do not push?
	uint32_t edi, esi, ebp, esp, ebx;
	uint32_t edx, ecx, eax;
} __attribute__((packed));




/** \brief IDT descriptor/entry */
class IDTDescriptor {
public:
	union {
		struct {
			uint16_t offset_1;
			uint16_t selector;
			uint8_t  zero;
			uint8_t  type_attr;
			uint16_t offset_2;
		} __attribute__((packed));

		uint64_t value; //!< raw descriptor contents
	} __attribute__((packed));

	/** \brief Constructor for empty descriptor */
	constexpr IDTDescriptor() : value(0) {};

	/** \brief Constructor for IDT descriptor */
	constexpr IDTDescriptor(uint32_t handler, uint16_t sel, uint8_t type) :
		offset_1(handler & 0x0000FFFF),
		selector(sel),
		zero(0),
		type_attr(type),
		offset_2(handler >> 16) {};
} __attribute__((packed));



/** \brief IDT register structure for `lidt` instruction */
struct InterruptDescriptorTable {
	uint16_t limit; //!< IDT size in bytes
	const IDTDescriptor* base; //!< IDT base address
} __attribute__((packed));



/** \brief Global IDT interface */
class IDT {
	/** \brief IDT register value */
	static const InterruptDescriptorTable idt;

	/** \brief Gate types */
	enum {
		TYPE_DPL0_IRQ_GATE = 0x8E,
		TYPE_DPL0_TRAP_GATE = 0x8F,
		TYPE_DPL3_IRQ_GATE = 0xEE
	};

public:
	/** \brief Initialize and enable the IDT */
	static void	init();
};

#endif

}; // namespace arch

#endif /* IDT_H_ */
