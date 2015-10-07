#include "constructors.h"
#include "timer.h"
#include "machine.h"


extern "C" {
	char __attribute__(( aligned (16) )) os_stack[1024];

	/** Initialisation stub for generic startup code */
	void init_generic();

	void arch_startup() {
		// run constructors of global objects
		run_constructors();

		// Enable soft interrupt source
		Machine::clear_csr_bit(mip, MIP_MSIP);
		//// Should be MIP_MSIE (same constant)
		Machine::set_csr_bit(mie, MIP_MSIP);

		// arch::Timer::init is called in StartOS

		init_generic();
	}
}
