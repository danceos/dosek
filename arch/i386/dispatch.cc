#include "idt.h"
#include "gdt.h"
#include "machine.h"
#include "paging.h"
#include "tcb.h"
#include "os/util/inline.h"
#include "os/util/assert.h"
#include "os/util/encoded.h"
#include "lapic.h"
#include "dispatch.h"

namespace arch {

extern TCB * const OS_tcbs[];

/** \brief Startup stackpointer (save location) */
volatile void* startup_sp = 0; // This location is write only
volatile uint32_t save_sp = 0;

#ifdef CONFIG_ARCH_PRIVILEGE_ISOLATION

#ifdef CONFIG_DEPENDABILITY_ENCODED
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
	#ifdef CONFIG_DEPENDABILITY_ENCODED
	// decode task ID
	uint16_t id = dispatch_task.decode();
	#else
	uint16_t id = dispatch_task;
	#endif

	// get TCB
	const TCB * const tcb = OS_tcbs[id];

	// set save_sp
#ifdef CONFIG_DEPENDABILITY_ENCODED
	save_sp = id | ((id) << 16);
#else
	save_sp = id;
#endif

#ifdef CONFIG_ARCH_MPU
	// set new page directory
	MMU::switch_task(id);
#endif

	void *ip;
	uint32_t *sp;
	Dispatcher::resolve_ip_and_sp(tcb, ip, sp);

	// send end-of-interrupt signal
	LAPIC::send_eoi();

	// exit system at IO privilege level 3 with IRQs disabled
	Machine::sysexit(ip, sp, 0x3000);
}

#endif

} // namespace arch
