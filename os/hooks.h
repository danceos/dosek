#ifndef __OS_KRN_HOOKS
#define __OS_KRN_HOOKS

#include "os/util/inline.h"

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

#define CALL_HOOK(NAME, ...) __OS_HOOK_ ## NAME (__VA_ARGS__)

#endif
