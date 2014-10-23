/**
 * @file
 * @ingroup i386
 * @brief i386 Interrupt structures
 */

#ifndef GIC_H_
#define GIC_H_

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


struct GIC_proc_t {
       uint32_t ICR;       // Interface Control Register
       uint32_t PMR;       // Priority Mask Register
       uint32_t BPR;       // Binary Point Register
       uint32_t IAR;       // Interrupt Acknowledge Register
       uint32_t EOIR;       // End of Interrupt Register
       uint32_t RPR;       // Running Priority Register
       uint32_t HPIR;       // Highest Pending Interrupt Register
       uint32_t ABPR;       // Aliased Binary Point Register
};

struct GIC_dist_t {
       unsigned int DCR;       // Distributor Control Register
       unsigned int ICTR;       // Interrupt Controller Type Register
       unsigned int IIDR;       // Distributor Implementer Identification Register
       unsigned int reserved0[29];
       unsigned int ISR[32];       // Interrupt Security Registers
       unsigned int ISER[32];       // Interrupt Set-Enable Registers
       unsigned int ICER[32];       // Interrupt Clear-Enable Registers
       unsigned int ISPR[32];       // Interrupt Set-Pending Registers
       unsigned int ICPR[32];       // Interrupt Clear-Pending Registers
       unsigned int IABR[32];       // Active Bit Registers
       unsigned int reserved1[32];
       unsigned int IPR[255];       // Interrupt Priority Registers
       unsigned int reserved2;
       unsigned int IPTR[255];       // Interrupt Process Targets Registers
       unsigned int reserved3;
       unsigned int ICFR[64];       // Interrupt Configuration Registers
       unsigned int reserved4[128];
       unsigned int SGIR;      // Software Generated Interrupt Register
       unsigned int reserved5[55];
       unsigned int IIR[12];       // Identification Registe
};

private:

    static forceinline void write_reg(gic_reg reg, uint32_t val) {
        *((volatile uint32_t*) reg) = val;
    }

    static forceinline uint32_t read_reg(gic_reg reg) {
        return *((volatile uint32_t*) reg);
    }


    static forceinline volatile GIC_proc_t& GICcpu(void) {
        return *reinterpret_cast<volatile GIC_proc_t*>(GIC_CPU_BASE);
    }


    static forceinline volatile GIC_dist_t& GICdist(void) {
        return *reinterpret_cast<volatile GIC_dist_t*>(GIC_DIST_BASE);
    }

public:
    /** \brief Initialize and enable the GIC */
    static void init();

    /** \brief Enable Distributor */
    static void init_dist(void) {
        GICdist().DCR = 0; // disable whole controller in order to write config

        for(int i = 0; i != cfIRQ_MAXHANDLERNUM / 32; ++i) {
            GICdist().ICER[i] = 0xFFFFFFFF;// disable interrupts
            if(i > 0) {
                GICdist().ICPR[i] = 0xFFFFFFFF; // clear interrupts
            }
        }

        for(int i = 0; i != cfIRQ_MAXHANDLERNUM / 4; ++i) {
            if(i > 7) {
                GICdist().IPR[i] = 0x0; // reset interrupt prios
            }
            GICdist().IPTR[i] = 0x0; // reset interrupt targets
        }

        // set interrupt configuration (level high sensitive, 1-N)
        for(int i = 2; i != cfIRQ_MAXHANDLERNUM / 16; ++i) {
            GICdist().ICFR[i] = 0x55555555;
        }

        GICdist().DCR = 1; // reenable distributor
    }

    /** \brief Enable CPU interface */
    static void init_proc(void) {
        // clear cpu specific distributor bits
        GICdist().ICPR[0] = 0xffffffff;
        for(int i = 0; i != 8; ++i) {
            GICdist().IPR[i] = 0;
        }

        GICdist().ICFR[0] = 0xaaaaaaaa;
        GICdist().ICFR[1] = 0x0; // level-sensitive, otherwise spurious interrupts

        // disable cpu interface in order to write configuration
        GICcpu().ICR = 0;
        // grouping disabled
        GICcpu().BPR = 0x07;

        // clear pending irqs
        do {
            uint32_t tmp = GICcpu().IAR;
            if((tmp & 0x3ff) == 0x3ff) {
                break;
            }
            GICcpu().EOIR = tmp;
        } while(1);

        // enable cpu interface
        // enable IRQs [0], FIRQs [1], and map Group1 to FIRQs [3]
        GICcpu().ICR = (1<<3) | (1<<1) | (1<<0);
    }

    /** \brief Enable the GIC (distributor and CPU interface) */
    static void enable() {
        init_dist();
        init_proc();
    }

    /** \brief Setup Interrupt */
    static void enable_irq(irq_id irq_num) {
        // setup priority mask, 0xffff lowest prio:
        // Any priority higher is serviced.
        GICcpu().PMR = 0xffff;

        if (irq_num >= 32) {
            GICdist().IPTR[irq_num/4] |= (1 << (irq_num % 8 ) * 8);
        }

        unmask_irq(irq_num);
    }

    static void unmask_irq(irq_id id) {
        GICdist().ISER[id / 32] |= 1 << (id % 32);
    }

    static void mask_irq(irq_id id) {
        GICdist().ICER[id / 32] |= 1 << (id % 32);
    }

    /** \brief Accept interrupt and get interrupt ID */
    static forceinline irq_id accept() {
        // accept the interrupt and read its ID

        irq_id id = GICcpu().IAR & 0xfff;

        //if(id & 0x1FF == 1023) spurious_interrupt();

        return id;
    }


    /** \brief Send end-of-interrupt signal */
    static forceinline void send_eoi(irq_id id) {
        GICcpu().EOIR = id;
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
        // distribute only to requesting (this) CPU: 0b10 at bit 24
        GICdist().SGIR = ((irq & 0xFF) | (2 << 24));
        //write_reg(GICD_SGIR, (irq & 0xFF) | (2 << 24));
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
#define IRQ_RESCHEDULE 1 //!< reschedule (AST) software interrupt
#define IRQ_DISPATCH 0 //!< dispatcher (AST) software interrupt
#define IRQ_LOCAL_TIMER 29 //!< local CPU timer interrupt
#define IRQ_WDT 30 //!< local watchdog timer interrupt
/**@}*/

/**
 * @name IRQ handler table
 *
 * In this table, we store the requested irq handlers. irq_handler
 * will indirectly call into this table.
 */
typedef void* (* const irq_handler_t)(void*, uint32_t);
extern "C"  __attribute__((section(".text.irq_handlers"))) irq_handler_t const irq_handlers[];


/**
 * @name IRQ handler table
 *
 * In this table, we store the requested irq handlers. irq_handler
 * will indirectly call into this table.
 */
typedef void* (* const irq_handler_t)(void*, uint32_t);
extern "C"  __attribute__((section(".text.irq_handlers"))) irq_handler_t const irq_handlers[];


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
 * To finish interrupt handling call arch::GIC::send_eoi(irqno). !
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
	extern "C" void* irq_handler_ ## irqno (void* __attribute__((unused)) task_sp, __attribute__((unused)) uint32_t irq)


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
	IRQ_HNDLR(irqno) {				\
		handler();					\
		arch::GIC::send_eoi(irqno);	\
		return task_sp;			\
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
	forceinline void irq_handler_fun_ ## irqno ();		\
	ISR_HANDLER(irqno, irq_handler_fun_ ## irqno)	\
    forceinline void irq_handler_fun_ ## irqno ()

/**@}*/

}; // namespace arch

/**
 * @name System IRQ handlers
 *
 * This are forward declarations to well-known system handlers.
 * These names are defined outside of any namespace.
 * 0 = Dispatcher
 * 1 = Rescheduler
 * 29 = Timer
 */
extern "C" void* irq_handler_0(void* task_sp, uint32_t id);
extern "C" void* irq_handler_1(void* task_sp, uint32_t id);
extern "C" void* irq_handler_29(void* task_sp, uint32_t id);
extern "C" void* irq_handler_unhandled(void* task_sp, uint32_t id);

#endif /* IRQ_AN_ */
