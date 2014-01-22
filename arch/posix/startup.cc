/**
 * @file
 * @ingroup posix
 * @brief Architecture-specific startup code
 */

#include "itimer.h"
#include "dispatch.h"

/** Initialisation stub for generic startup code */
extern void init_generic();

using namespace arch;

//!< i386 specific startup code
void arch_startup()
{
    // global constructors habe been are already called before main.

    Machine::init();

    Dispatcher::init();

    // setup timer
    ITimer::init();

	// Proceed to generic initialisation
	init_generic();
}

//!< POSIX startup obviously in "main"
//!< Here, all constructors are already called.

int main(int argc, char**argv){
    (void) argc;
    (void) argv;
    arch_startup();
    return 0;
}
