#include "output.h"
#include "machine.h"
#include "timer.h"
#include "interrupt.h"
#include "os/scheduler/scheduler.h"



#ifndef CONFIG_OS_SYSTEMCALLS_WIRED
static bool ast_requested;
static int ast_level;

void arch::request_reschedule_ast() {
	ast_requested = true;
}

bool arch::in_syscall() {
	return ast_level == 0;
}
#endif

unsigned char Machine::soft_irq_cause;

extern "C" void bad_trap() {
	kout << "machine mode: unhandlable trap "
		<< hex << Machine::read_csr(mcause) << " @ "
		<< Machine::read_csr(mepc) << endl;
	Machine::shutdown();
}

void arch::bad_soft_irq(unsigned char cause) {
	kout << "machine mode: unhandlable soft_irq "
		 << hex << cause << " @ " << Machine::read_csr(mepc) << endl;
	Machine::shutdown();
}


extern "C" void interrupt_handler(long long mcause, uintptr_t sp) {
#ifndef CONFIG_OS_SYSTEMCALLS_WIRED
	ast_level ++;
#endif

	(void) sp;
	if (mcause < 0) { // Interrupt
		uintptr_t device = mcause & 0xffffffff;
		if (device == 2) { // htif
			uintptr_t fromhost = Machine::swap_csr(mfromhost, 0);
			if (fromhost == 0) {
				goto out;
			}
			kout << "htif interrupt " << hex << fromhost << endl;
			bad_trap();
		} else if (device == 1) {
			arch::Timer::tick();
			goto out;
		} else if (device == 0) {
			// ack the interrupt;
			// kout << "Soft IRQ " << Machine::soft_irq_cause << endl;
			Machine::clear_csr_bit(mip, MIP_MSIP);
			arch::isr_table[Machine::soft_irq_cause](Machine::soft_irq_cause);
			goto out;
		}
		kout << "device " << device << endl;
		bad_trap();
	} else {
		kout << "trap" << endl;
		bad_trap();
	}
out:
#ifndef CONFIG_OS_SYSTEMCALLS_WIRED
	ast_level --;
	if (ast_requested) {
		ast_requested = false;
		__OS_ASTSchedule(0);
	}
#endif
	return;
}
