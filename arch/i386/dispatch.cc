#include "idt.h"
#include "gdt.h"
#include "machine.h"
#include "paging.h"
#include "tcb.h"
#include "os/util/inline.h"
#include "os/util/assert.h"
#include "os/util/encoded.h"
#include "lapic.h"

namespace arch {

extern TCB * const OS_tcbs[];

/** \brief Startup stackpointer (save location) */
volatile void* startup_sp = 0;
volatile uint32_t save_sp = 0;

#ifdef ENCODED
volatile Encoded_Static<A0, 42> dispatch_task;
#else
volatile uint16_t dispatch_task;
#endif

/** \brief Dispatch interrupt handler
 *
 * This interrupt is called after the next task is determined by the scheduler in ring 3
 * and performs the actual dispatching in ring 0.
 */
IRQ_HANDLER(IRQ_DISPATCH) {
	#ifdef ENCODED
	// decode task ID
	uint16_t id = dispatch_task.decode();
	#else
	uint16_t id = dispatch_task;
	#endif

	// get TCB
	const TCB * const tcb = OS_tcbs[id];

	// set save_sp
#ifdef ENCODED
	save_sp = id | ((id) << 16);
#else
	save_sp = id;
#endif

	// set new page directory
	MMU::switch_task(id);


	// push instruction pointer
	void* ip;
	uint32_t *sp = (uint32_t *) tcb->get_sp();
	assert(tcb->check_sp());

	if(tcb->is_running()) {
		// resume from saved IP on stack
		// requires new page directory set before!
		void * _ipv = (void*) *(sp - 1);
#ifdef ENCODED
		const os::redundant::HighParity<void *> ipv(_ipv);
#else
		const os::redundant::Plain<void *> ipv(_ipv);
#endif

		assert(ipv.check());
		ip = ipv.get();

		*(sp - 1) = 0; // clear IP to prevent this from remaining valid in memory
	} else {
		// start function from beginning
		ip = (void*) tcb->fun;
	}

	// send end-of-interrupt signal
	LAPIC::send_eoi();

	// exit system at IO privilege level 3 with IRQs disabled
	Machine::sysexit(ip, sp, 0x3000);
}

} // namespace arch
