#include "machine.h"
#include "syscall.h"

using namespace arch;

// new syscall to trigger interrupt using local APIC
// for now, any function can be called using syscall(),
// so it is easy to add this for this test.
noinline void __OS_trigger_syscall() {
	uint8_t irq;
	asm volatile("" : "=a"(irq));
	Machine::trigger_interrupt(irq);
}

void Machine::trigger_interrupt_from_user(uint8_t irq) {
	arch::syscall<true>(__OS_trigger_syscall, irq);
}

