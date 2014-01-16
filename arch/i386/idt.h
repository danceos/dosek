/**
 * @file
 * @ingroup i386
 * @brief i386 Interrupt structures
 */

#ifndef IDT_H_
#define IDT_H_

#include "stdint.h"

namespace arch {

/**
 * @name IRQ numbers
 * @{
 */
#define IRQ_SYSCALL 33 //!< syscall software interrupt
#define IRQ_DISPATCH 32 //!< dispatcher software interrupt
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
	extern "C" __attribute__((naked)) void irq_handler_ ## irqno (void)


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
	extern "C" __attribute__((naked)) void isr_ ## irqno (void) { \
		struct task_context* ctx; \
		asm("" : "=S"(ctx)); \
		handler(ctx); \
		asm volatile("jmp handler_exit" :: "S"(ctx)); \
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
	forceinline void irq_handler_fun_ ## irqno (struct task_context* ctx); \
	ISR_HANDLER(irqno, irq_handler_fun_ ## irqno); \
	forceinline void irq_handler_fun_ ## irqno (__attribute__((unused)) struct task_context* ctx)
/**@}*/



/** \brief Context saved by CPU on interrupt/trap/syscall */
struct cpu_context {
	uint32_t eip; //!< source address
	uint32_t cs; //!< source code segment selector

	uint32_t eflags; //!< original flags

	// only pushed when coming from ring>0:
	uint32_t user_esp; //!< userspace stack pointer
	uint32_t ss; //!< userspace stack segment selector
} __attribute__((packed));

/** \brief Application context (saved by IRQ handlers) */
struct task_context {
	// saved registers
	// TODO: dont save eax, ecx, edx (caller save) when syscalling?
	uint32_t edi, esi, ebp, esp, ebx;
	uint32_t edx, ecx, eax;

	// pushed by CPU or handler:
	uint32_t error_code; //!< error code (dummy value if unused)

	cpu_context cpu_context; //!< context saved by CPU
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

}; // namespace arch

#endif /* IDT_H_ */
