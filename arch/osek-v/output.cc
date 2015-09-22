#include "machine.h"
#include "frontend.h"
#include "output.h"

HTIFOutputStream kout;

void noinline HTIFOutputStream::putchar(char ch) {
	bool interrupts = Machine::disable_interrupts();
	while (Machine::swap_csr(mtohost, TOHOST_CMD(1, 1, ch)) != 0);
	while (1) {
		uintptr_t fromhost = Machine::read_csr(mfromhost);
		if (FROMHOST_DEV(fromhost) != 1 || FROMHOST_CMD(fromhost) != 1) {
			if (fromhost) {}
			// htif_interrupt(0, 0);
			continue;
		}
		Machine::write_csr(mfromhost, 0);
		break;
	}
	if (interrupts)
		Machine::enable_interrupts();
}
