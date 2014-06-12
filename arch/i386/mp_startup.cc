
#include "arch/generic/hardware_threads.h"
#include "mp.h"

namespace arch {

	/* Entry point for cpu startup */
	bool start_hardware_thread(unsigned int hardware_number,
	                           void *bottom_of_stack,
	                           unsigned int size_of_stack,
	                           void (*startup_function)())
	{
		return boot_cpu(hardware_number, bottom_of_stack, size_of_stack, startup_function);
	}

}

volatile int cpu_started;
void(* volatile mp_startup_function)();

/* Exit point after the initialization of the cpu */
extern "C" void mp_startup()
{
	void (*startup_function)() = mp_startup_function;
	cpu_started = 1;
	startup_function();
}



