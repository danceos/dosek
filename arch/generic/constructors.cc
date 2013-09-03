#include "constructors.h"

extern "C" {
	extern void (*__CTORS_START)();
	extern void (*__CTORS_END)();

	void run_constructors() {
		// Call constructors of all global object instances.
		for( void (**ctor)() = &__CTORS_START; ctor != &__CTORS_END; ++ctor )
			(*ctor)();
	}
}
