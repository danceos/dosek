#ifndef __OS_KRN_HELPER
#define __OS_KRN_HELPER
/**
 * @file
 * @ingroup os
 * @brief Helper functions not defined in OSEK, that can be called
 * from the application
 */

#ifdef __cplusplus
extern "C" {
#endif
	/** \brief Shutdown the machine instantly */
	extern void ShutdownMachine(void);

#ifdef __cplusplus
}
#endif


#endif
