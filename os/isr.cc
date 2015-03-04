#include "os.h"
#include "machine.h"

/**
 * \brief Methods for interrupt disabling/enabling. This pair cannot
 *        be stacked.
 **/
void OSEKOS_DisableAllInterrupts() {
	Machine::disable_interrupts();
}

void OSEKOS_EnableAllInterrupts() {
	Machine::enable_interrupts();
}

/**
 * \brief Same as disable/enable but can be stacked.
 **/
static int __all_isr_count;
void OSEKOS_SuspendAllInterrupts() {
	Machine::disable_interrupts();
	__all_isr_count++;
}

void OSEKOS_ResumeAllInterrupts() {
	__all_isr_count--;
	if (__all_isr_count == 0) {
		Machine::enable_interrupts();
	}
}

static int __os_isr_count;

void OSEKOS_SuspendOSInterrupts() {
	Machine::disable_interrupts();
	__os_isr_count++;

}

void OSEKOS_ResumeOSInterrupts() {
	__os_isr_count--;
	if (__os_isr_count == 0) {
		Machine::enable_interrupts();
	}
}
