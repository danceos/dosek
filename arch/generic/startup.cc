/**
 * @file
 * @ingroup generic
 * @brief Common generic startup
 */

extern "C" void os_main(void);

//! @brief Prepare system environment
extern "C" void init_generic (void)
{
    //! @todo Here we might need some hardware init hook.

    //! We are now ready to run a C/C++ system.
	os_main();
}

