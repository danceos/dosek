#ifndef __OSEKOS_INTERRUPT_H__
#define __OSEKOS_INTERRUPT_H__

namespace arch{
	typedef void (*interrupt_handler_t)(unsigned char);
	extern interrupt_handler_t isr_table[];

	void bad_soft_irq(unsigned char);

	bool in_syscall();
}

#endif
