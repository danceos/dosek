/**
 * @file
 * @ingroup i386
 * @brief i386 interrupt handling
 */

#include "irq.h"
//#include "gdt.h"
//#include "exception.h"
#include "machine.h"
//#include "lapic.h"
#include "output.h"

#define CONTINUE_UNHANDLED_IRQ 0

namespace arch {

void GIC::init() {
    enable();
}

extern "C" uint32_t test_handler_1(uint32_t return_address, uint32_t id) {
    kout << "! " << (int) id << endl;
    GIC::send_eoi(id);
    return return_address;
}

extern "C" uint32_t test_handler_2(uint32_t return_address, uint32_t id) {
    kout << "! " << (int) id << endl;
    GIC::send_eoi(id);
    return return_address;
}

extern "C" uint32_t test_handler_3(uint32_t return_address, uint32_t id) {
    kout << "! " << (int) id << endl;
    GIC::send_eoi(id);
    return return_address;
}

extern "C" uint32_t test_handler_4(uint32_t return_address, uint32_t id) {
    kout << "! " << (int) id << endl;
    GIC::send_eoi(id);
    return return_address;
}

extern "C" __attribute__((naked)) void irq_exit(uint32_t return_address) {
    asm volatile("mov lr, %0" :: "r"(return_address));
    asm volatile("pop {r0, r1, r2, r3}");
    asm volatile("subs pc, lr, #0");

    Machine::unreachable();
}

extern "C" uint32_t irq_handler_0(uint32_t return_address, uint32_t id);

typedef uint32_t (* const fptr_t)(uint32_t, uint32_t);
extern "C"  __attribute__((section(".text.irq_handlers"))) constexpr fptr_t const handlers[] = {
    irq_handler_0,
    test_handler_1,
    test_handler_2,
    test_handler_3,
    test_handler_4
};


// test IRQ handler
extern "C" __attribute__((naked)) void irq_handler(uint32_t return_address) {
    //irq_id id = GIC::accept();
    asm volatile("ldr r1, [%0]" :: "r"(GIC::GICC_IAR) : "r0","r1"); // read IRQ info
    asm volatile("bfc r1, #12, #20" ::: "r0","r1"); // get interrupt number only

    //handlers[id](return_address, id);
    asm volatile("mov lr, irq_exit");
    asm volatile("ldr pc, [%0, +r1, LSL #2]" :: "r"(handlers) : "r0","r1");
/*
    //kout << "! " << (int) id << endl;
    GIC::send_eoi(id);

    asm volatile("mov lr, %0" :: "r"(return_address));
    asm volatile("pop {r0, r1, r2, r3}");
    asm volatile("subs pc, lr, #0");
*/
    Machine::unreachable();
}


// kernel panic dump
struct panic_frame {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t r7;
    uint32_t r8;
    uint32_t r9;
    uint32_t r10;
    uint32_t r11;
    uint32_t r12;

    uint32_t pc;
};
extern "C" void kernel_dump(panic_frame* pf) {
    kout << endl << "=== PANIC ===" << endl;

    //kout << "frame @ 0x" << pf << endl;


    kout << "PC:  " << hex << pf->pc << endl;
    kout << endl;

    kout << "r0:  " << hex << pf->r0 << endl;
    kout << "r1:  " << hex << pf->r1 << endl;
    kout << "r2:  " << hex << pf->r2 << endl;
    kout << "r3:  " << hex << pf->r3 << endl;
    kout << "r4:  " << hex << pf->r4 << endl;
    kout << "r5:  " << hex << pf->r5 << endl;
    kout << "r6:  " << hex << pf->r6 << endl;
    kout << "r7:  " << hex << pf->r7 << endl;
    kout << "r8:  " << hex << pf->r8 << endl;
    kout << "r9:  " << hex << pf->r9 << endl;
    kout << "r10: " << hex << pf->r10 << endl;
    kout << "r11: " << hex << pf->r11 << endl;
    kout << "r12: " << hex << pf->r12 << endl;
    kout << endl;

    uint32_t psr = Machine::get_spsr();
    kout << "PSR: " << hex << psr << endl;

    Machine::mode_t mode = (Machine::mode_t ) (psr & 0x1F);
    switch(mode) {
        case Machine::USER:
            kout << "     (user)" << endl;

            break;
        case Machine::FIQ:
            kout << "     (FIQ)" << endl;

            break;
        case Machine::IRQ:
            kout << "     (IRQ)" << endl;

            break;
        case Machine::SUPERVISOR:
            kout << "     (svc)" << endl;

            break;
        case Machine::ABORT:
            kout << "     (abort)" << endl;

            break;
        case Machine::UNDEFINED:
            kout << "     (undefined)" << endl;

            break;
        case Machine::SYSTEM:
            kout << "     (system)" << endl;

            break;
        default:
            kout << "     (mode: " << dec << mode << " ?!)" << endl;

            break;
    };
    kout << endl;

    uint32_t sp, lr;
    Machine::mode_t own_mode = (Machine::mode_t) (Machine::get_cpsr() & 0x1F);
    if(mode == Machine::USER) {
        mode = Machine::SYSTEM;
    }

    Machine::set_cpsr((Machine::get_cpsr() & ~(0x1F)) | mode);
    asm volatile("mov %0, sp; mov %1, lr" : "=r"(sp), "=r"(lr));
    Machine::set_cpsr((Machine::get_cpsr() & ~(0x1F)) | own_mode);

    kout << "SP:  " << hex << sp << endl;
    kout << "LR:  " << hex << lr << endl;

    kout << "=============" << endl;
}

#if 0
/** \brief Default handler for interrupts */
ISR(unhandled) {
	// interrupt number passed in %eax
	uint32_t intno;
	asm volatile("" : "=a"(intno));

	// print and halt when debugging
	#if DEBUG
	uint32_t ip = cpu->eip;
	debug << "unhandled interrupt ";
	debug << dec << intno;
	debug << " @ 0x";
	debug << hex << ip;
	debug << endl;

	asm("hlt");
	#endif

	#if CONTINUE_UNHANDLED_IRQ
	// send end-of-interrupt (unless exception)
	if(intno > 31) LAPIC::send_eoi();
	#else // CONTINUE_UNHANDLED_IRQ
	// panic on unhandled interrupts
	Machine::panic();
	#endif // CONTINUE_UNHANDLED_IRQ
}



// NMI error handler
IRQ_HANDLER(2) {
	// TODO: anything useful left to do?
	debug << "PANIC" << endl;

	Machine::halt();
}



extern "C" IDTDescriptor theidt[256];
constexpr InterruptDescriptorTable IDT::idt __attribute__ ((aligned (8))) = {
	sizeof(theidt)-1,
	&theidt[0]
};


void IDT::init() {
	// load static IDT
	asm volatile("lidt %0" : : "m"(IDT::idt) : "memory");
}
#endif

}; // namespace arch
