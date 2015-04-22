#include "gic.h"
#include "machine.h"
#include "tcb.h"
#include "os/util/inline.h"
#include "os/util/assert.h"
#include "os/util/encoded.h"

namespace arch {

extern TCB * const OS_tcbs[];

/** \brief Startup stackpointer (save location) */
volatile void* startup_sp = 0;

static uint32_t _save_sp = 0;

#ifdef CONFIG_DEPENDABILITY_ENCODED
os::redundant::MergedDMR<uint32_t> save_sp(_save_sp);
volatile Encoded_Static<A0, 42> dispatch_task;
#else
os::redundant::Plain<uint32_t> save_sp(_save_sp);
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
	if (save_sp.get() != 0) {
		CALL_HOOK(FaultDetectedHook, LOGIC_ERRORdetected, 0, 0);
	}
	save_sp.set(id);

	// set new page directory
	//MMU::switch_task(id);

	// push instruction pointer
	void* ip;
	uint32_t *sp = (uint32_t *) tcb->get_sp();
	tcb->check_sp();

	// send end-of-interrupt signal
	GIC::set_task_prio(IRQ_PRIO_LOWEST);

	if(tcb->is_running()) {
		// resume from saved IP on stack
		// requires new page directory set before!
		uint32_t ip = (uint32_t) *(sp - 1);
#ifdef CONFIG_DEPENDABILITY_ENCODED
		uint32_t ip2 = (uint32_t) *(sp - 2);
		if (ip != ip2) {
			CALL_HOOK(FaultDetectedHook, DMRdetected, ip, ip2);
		}
		// clear IP to prevent this from remaining valid in memory
		*(sp - 2) = 0;
#endif
		// clear IP to prevent this from remaining valid in memory
		*(sp - 1) = 0;

		// kout << "D: " << id << " " << ip << " " << sp << endl;

		// Set the user's stack pointer
		// We leave to the user mode in system mode
		asm volatile("mov r1, %0;"
					 "mov r0, %1;"
					 "bx r1" :: "l"(ip), "l"(sp) : "r0", "r1");
	} else {
		// start function from beginning
		ip = (void*) tcb->fun;

		//kout << "D(S): " << id << " " << ip << " " << sp << endl;


		// Set the user's stack pointer
		// We leave to the user mode in system mode
		asm volatile("mov r1, %0;"
					 "mov r0, %1;"
					 "cps #31;"
					 "mov sp, r0;"
					 "bx r1" :: "l"(ip), "l"(sp) : "r0", "r1");

	}
    Machine::unreachable();
	return 0;
}

} // namespace arch
