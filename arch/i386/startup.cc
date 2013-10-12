/**
 * @file
 * @ingroup i386
 * @brief Architecture-specific startup code
 */

#if !defined(__cplusplus)
#include <stdbool.h> /* C doesn't have booleans by default. */
#endif
#include <stddef.h>
#include <stdint.h>

/* Check if the compiler thinks if we are targeting the wrong operating system. */
#if defined(__linux__)
//#error "You are not using a cross-compiler, you will most certainly run into trouble"
#endif

/** Initialisation stub for generic startup code */
extern void init_generic();

//!< i386 specific startup code
extern "C" void arch_startup()
{
    // do some hw init here.
    
    // Proceed to generic initialisation
	init_generic();
}
