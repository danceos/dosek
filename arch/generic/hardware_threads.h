#ifndef __HARDWARE_THREADS_H__
#define __HARDWARE_THREADS_H__

namespace arch {
	/**
	 * \brief Starts another hardware thread (generic interface)
	 *
	 * \param hardware_number Identifies the hardware element that is started
	 * \param bottom_of_stack The bottom (lowest address) of the stack for the
	 *                        hardware stack
	 * \param size_of_stack The size of the given stack
	 * \param startup_function A function pointer to the function that will be
	 *                         run on the started hardware thread
	 * \return true if everything went fine, false on error
	 **/
	bool start_hardware_thread(unsigned int hardware_number,
	                           void *bottom_of_stack,
	                           unsigned int size_of_stack,
	                           void (*startup_function)());
}

#endif
