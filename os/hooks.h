#ifndef __OS_KRN_HOOKS
#define __OS_KRN_HOOKS

#include "os/util/inline.h"
#include <stdint.h>

/**
 * @file
 * @ingroup os
 * @brief Here are function declarations for hooks, that are called
 * from within the system level, and can be filled by the
 * application. The Generator has to generate this functions!
 */

/**
 * \brief Called directly before the idle loop starts.
 */
EXTERN_C_DECL void __OS_HOOK_PreIdleHook(void);
EXTERN_C_DECL inlinehint void __OS_HOOK_DEFINED_PreIdleHook(void);

#define PreIdleHook() \
	void __OS_HOOK_DEFINED_PreIdleHook(void)



typedef enum DetectedFault_t {
	XORdetected = 1,
	DMRdetected = 2,
	ANBdetected = 3,
} DetectedFault_t;


EXTERN_C_DECL void __OS_HOOK_FaultDetectedHook(DetectedFault_t, uint32_t, uint32_t);
EXTERN_C_DECL inlinehint void __OS_HOOK_DEFINED_FaultDetectedHook(DetectedFault_t, uint32_t, uint32_t);

#define FaultDetectedHook() \
	void __OS_HOOK_DEFINED_FaultDetectedHook(DetectedFault_t type, uint32_t arg1, uint32_t arg2)


#define CALL_HOOK(NAME, ...) __OS_HOOK_ ## NAME (__VA_ARGS__)

#endif
