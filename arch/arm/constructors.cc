/**
 * @file
 * @ingroup generic
 * @brief Invoke global objects' constructors
 */

#include "constructors.h"

extern "C" {
    //! Address of the first global constructor (Defined by the linker script)
    extern void (*__CTORS_START)(void);
    //! Address of the last global constructor (Defined by the linker script)
    extern void (*__CTORS_END)(void);

	extern char _erom, _data, _edata, _bstart, _bend;

    void run_constructors(void) {
		char *src = &_erom;
		volatile char *dst = &_data;

		/* ROM has data at end of text; copy it. */
		while (dst < &_edata) {
			*dst++ = *src++;
		}

		/* Zero bss */
		for (dst = &_bstart; dst< &_bend; dst++) {
			*dst = 0;
		}


        //! Call constructors of all global object instances.
        //! @note Ensure that your linker script places
        //!       all `CTORS` between `__CTORS_START` and
        //! `__CTORS_END`
        for( void (** volatile ctor)() = &__CTORS_START; ctor != &__CTORS_END; ++ctor ) {
            (*ctor)();
		}
	}
}
