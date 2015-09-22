#include "timer.h"
#include "machine.h"
#include "os/counter.h"


namespace arch {

void Timer::init() {
	reload();
    // Enable the timer interrupt
	Machine::set_csr_bit(mie, MIP_MTIP);
}

void Timer::reload() {
	uintptr_t time = Machine::read_csr(mtime);
	Machine::write_csr(mtimecmp, time + 2);
}

void Timer::tick() {
	reload();
	os::Counter::tick();
}


}
