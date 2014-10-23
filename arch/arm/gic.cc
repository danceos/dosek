/**
 * @file
 * @ingroup i386
 * @brief i386 interrupt handling
 */

#include "gic.h"
#include "machine.h"
#include "dispatch.h"
#include "output.h"

#define CONTINUE_UNHANDLED_IRQ 0

namespace arch {

extern void ** const OS_stackptrs[];

void GIC::init() {
    enable();
}

extern "C" void * irq_handler_unhandled(void* task_sp, uint32_t id) {
    //kout << "! " << (int) id << endl;
    GIC::send_eoi(id);
    return task_sp;
}

// IRQ gate
extern "C" void * irq_handler(void * task_sp) {
    irq_id id = GIC::accept();
	// void *lr;
	// asm volatile("mov %0, lr" : "=r"(lr) ::);

	// kout << "#" << (save_sp & 0xffff) << " " << task_sp << " " << id
	// 	 << "% " << (void*)((uint32_t *)task_sp)[-1] 
	// 	 << ": " << lr
	// 	 << endl;

    // asm volatile("ldr r1, [%0]" :: "r"(GIC::GICC_IAR) : "r0", "r1"); // read IRQ info
    // asm volatile("bfc r1, #12, #20" ::: "r0", "r1"); // place interrupt number in r1

    // save stack pointer
    uint32_t ssp = save_sp;
	if (ssp != 0) {
		assert( (ssp & 0xFFFF) == (ssp >> 16) );
		*OS_stackptrs[ssp & 0xFFFF] = task_sp;
	}

    void* ret = irq_handlers[id](task_sp, id);


	return ret;
	//asm volatile("mov r0, %0" :: "r"(task_sp) : "r0", "r1");
	//asm volatile("mov r1, %0" :: "r"(id) : "r0", "r1");
    //asm volatile("ldr pc, [%0, +%1, LSL #2]" :: "r"(handlers), "r"(id): "r0","r1");

    //Machine::unreachable();
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

#endif

}; // namespace arch
