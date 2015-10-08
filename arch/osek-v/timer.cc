#include "timer.h"
#include "machine.h"
#include "os/counter.h"


namespace arch {

unsigned Timer::interval;

void Timer::init(unsigned interval_ms) {
	interval = interval_ms;
	reload();
    // Enable the timer interrupt
	Machine::set_csr_bit(mie, MIP_MTIP);
}

void Timer::reload() {
	uintptr_t time = Machine::read_csr(mtime);
	Machine::write_csr(mtimecmp, time + 64 * interval);
}

void Timer::tick() {
	reload();
	os::Counter::tick();
}


}
