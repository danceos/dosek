
#include "constructors.h"

extern void arch_startup(void);

extern void os_main(void);

// prepare system environment
extern "C" void init_generic (void)
{
	// Call constructors of all global object instances.
	run_constructors();

	// Architecture specific startup
	arch_startup();

	// We are now ready to run a C/C++ system.
	os_main();
}

