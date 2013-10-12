/**
 * @file
 * @ingroup generic
 * @brief Common generic startup
 */

#include "constructors.h"

extern void os_main(void);

//! @brief Prepare system environment
void init_generic (void)
{
	//! Call constructors of all global object instances.
	run_constructors();

    //! @todo Here we might need some hardware init hook.

    //! We are now ready to run a C/C++ system.
	os_main();
}

