#include "idt.h"
#include "gdt.h"
#include "machine.h"
#include "paging.h"
#include "os/util/inline.h"
#include "lapic.h"

namespace os {
/** \brief Startup stackpointer (save location) */
void* startup_sp = 0;
void** save_sp = &startup_sp;
};

namespace arch {

/** \brief Dispatch interrupt handler
 *
 * This interrupt is called after the next task is determined by the scheduler in ring 3
 * and performs the actual dispatching in ring 0.
 */
IRQ_HANDLER(IRQ_DISPATCH) {
	// get arguments and saved context from registers
	uint32_t id; // from %edx
	uint32_t sp; // from %ebx
	uint32_t fun; // from %ecx
	cpu_context *ctx; // stored at current stack pointer
	asm volatile("mov %%esp, %0" : "=r"(ctx), "=b"(sp), "=c"(fun), "=d"(id));

	// TODO: remove/reuse pushed CPU context?

	// push stack segment, DPL3
	Machine::push(GDT::USER_DATA_SEGMENT | 0x3);

	// push stack pointer
	Machine::push(sp);

	// push flags, IO privilege level 3
	// TODO: always enable interrupts?
	Machine::push(ctx->eflags | 0x3000);

	// push code segment, DPL3
	Machine::push(GDT::USER_CODE_SEGMENT | 0x3);

	// set new page directory
	MMU::switch_task(id);

	// set userspace segment selectors
	// TODO: maybe not neccessary?
	Machine::set_data_segment(GDT::USER_DATA_SEGMENT | 0x3);

	// push instruction pointer
	if(fun >= 0x200000) {
		// resume from saved IP on stack
		// requires new page directory set before!
		uint32_t ip = *(*((uint32_t**) fun) - 1);
		Machine::push(ip);
	} else {
		// start function from beginning
		Machine::push(fun);
	}

	// TODO: check prepared stack? (SSE crc32q?)

	// return from interrupt
	Machine::return_from_interrupt();
}

} // namespace arch