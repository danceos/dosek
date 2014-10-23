#include "machine.h"
#include "syscall.h"

using namespace arch;


void Machine::trigger_interrupt(uint8_t irq) {
	arch::GIC::trigger(irq);
}


void Machine::trigger_interrupt_from_user(uint8_t irq) {
	arch::GIC::trigger(irq);
	/* We add this loop here, since QEMU triggers software generated
	   interrupts only with a large delay. For details on this bug, see:

	   http://lists.gnu.org/archive/html/qemu-discuss/2014-03/msg00028.html
	 */
	volatile int i = 0;
	while (i < 1000) i++;
}

