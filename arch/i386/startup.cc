#if !defined(__cplusplus)
#include <stdbool.h> /* C doesn't have booleans by default. */
#endif
#include <stddef.h>
#include <stdint.h>

/* Check if the compiler thinks if we are targeting the wrong operating system. */
#if defined(__linux__)
//#error "You are not using a cross-compiler, you will most certainly run into trouble"
#endif

#include "MemoryInfo.h"

struct globalConstructorTest {
	int foo;

	globalConstructorTest() {
		foo = 1;
	}
};

MemoryInfo meminfo;


extern void init_generic();

globalConstructorTest tester;

extern "C" void arch_startup(multiboot_info_t* p_mb, unsigned int multiboot_magic)
{
	meminfo.setup(p_mb);

	init_generic();
}
