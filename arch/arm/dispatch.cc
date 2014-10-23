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
extern "C" volatile uint32_t save_sp = 0;

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
	assert(save_sp == 0);
	save_sp = id | ((id) << 16);

	// set new page directory
	//MMU::switch_task(id);

	// push instruction pointer
	void* ip;
	uint32_t *sp = (uint32_t *) tcb->get_sp();
	//assert(tcb->check_sp());

	if(tcb->is_running()) {
		// resume from saved IP on stack
		// requires new page directory set before!
		uint32_t ipv = (uint32_t) *(sp - 1);

		//assert(__builtin_parity(ipv) == 1);
		ip = (void*) ((ipv & 0x7FFFFFFF));

		*(sp - 1) = 0; // clear IP to prevent this from remaining valid in memory
	} else {
		// start function from beginning
		ip = (void*) tcb->fun;

	}

	//kout << "D: " << id << " " << ip << " " << sp << endl;

	// send end-of-interrupt signal
	GIC::send_eoi(IRQ_DISPATCH);

	// Set the user's stack pointer
	// We leave to the user mode in system mode
	Machine::switch_mode(Machine::SYSTEM);
	asm volatile("mov sp, %0" :: "r"(sp));
    asm volatile("mov r0, %0" :: "r"(sp) : "r0");
    asm volatile("bx %0" :: "r"(ip));
    Machine::unreachable();
	return 0;
}

} // namespace arch
