#include "machine.h"
#include "syscall.h"

using namespace arch;


void Machine::trigger_interrupt(uint8_t irq) {
	arch::GIC::trigger(irq);
}


void Machine::trigger_interrupt_from_user(uint8_t irq) {
	arch::GIC::trigger(irq);
}

