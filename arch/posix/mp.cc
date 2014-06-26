
#include "arch/generic/hardware_threads.h"
#include <pthread.h>

static void *pthread_wrapper(void* function)
{
	void (*startup_function)() = reinterpret_cast<void(*)()>(function);
	startup_function();
	return nullptr;
}

namespace arch
{
	bool start_hardware_thread(unsigned int hardware_number,
	                           void *bottom_of_stack,
	                           unsigned int size_of_stack,
	                           void (*startup_function)())
	{
		/* These parameter are not required, since on posix there is already
		 * an operating system handling the stack and cpu startup. */
		(void) hardware_number;
		(void) bottom_of_stack;
		(void) size_of_stack;
		pthread_t thread;
		int error = pthread_create(&thread, nullptr, pthread_wrapper, reinterpret_cast<void*>(startup_function));
		pthread_detach(thread);
		return !error;
	}
}


