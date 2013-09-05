
#include "constructors.h"

extern void os_main(void);

// prepare system environment
void init_generic (void)
{
	// Call constructors of all global object instances.
	run_constructors();

  // We are now ready to run a C/C++ system.
	os_main();
}

