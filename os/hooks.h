#ifndef __OS_KRN_HOOKS
#define __OS_KRN_HOOKS

#include "os/util/inline.h"
#include <stdint.h>
#include "os/osek_types.h"

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
	__OS_HOOK_DEFINED_PreIdleHook(void)

/**
 * \brief Called in StartOS().
 */
EXTERN_C_DECL void __OS_HOOK_StartupHook(void);
EXTERN_C_DECL inlinehint void __OS_HOOK_DEFINED_StartupHook(void);

#define StartupHook() \
	__OS_HOOK_DEFINED_StartupHook(void)


/**
 * \brief Currently called in Tasks kickoff().
 * Should be called before a task enters RUNNING state.
 */
EXTERN_C_DECL void __OS_HOOK_PreTaskHook(void);
EXTERN_C_DECL inlinehint void __OS_HOOK_DEFINED_PreTaskHook(void);

#define PreTaskHook() \
	__OS_HOOK_DEFINED_PreTaskHook(void)


/**
 * \brief Called on context switch when tasks leave RUNNING state.
 */
EXTERN_C_DECL void __OS_HOOK_PostTaskHook(void);
EXTERN_C_DECL inlinehint void __OS_HOOK_DEFINED_PostTaskHook(void);

#define PostTaskHook() \
	__OS_HOOK_DEFINED_PostTaskHook(void)

/**
 * \brief Called on ShutdownOS
 */
EXTERN_C_DECL void __OS_HOOK_ShutdownHook(StatusType);
EXTERN_C_DECL inlinehint void __OS_HOOK_DEFINED_ShutdownHook(StatusType);

#define ShutdownHook(status)							\
	__OS_HOOK_DEFINED_ShutdownHook(status)


typedef enum DetectedFault_t {
	XORdetected = 1,
	DMRdetected = 2,
	ANBdetected = 3,
	PARITYdetected = 4,
	APPdetected = 5,
	TRAPdetected = 6,
	IRQ_SPURdetected = 7,
	LOGIC_ERRORdetected = 8,
	STATE_ASSERTdetected = 9,
	RETRY_ERRORdetected = 10,
	TMRdetected = 11,
} DetectedFault_t;


EXTERN_C_DECL void __OS_HOOK_FaultDetectedHook(DetectedFault_t, uint32_t, uint32_t);
EXTERN_C_DECL inlinehint void __OS_HOOK_DEFINED_FaultDetectedHook(DetectedFault_t, uint32_t, uint32_t);

#define FaultDetectedHook() \
	__OS_HOOK_DEFINED_FaultDetectedHook(DetectedFault_t type, uint32_t arg1, uint32_t arg2)


#define CALL_HOOK(NAME, ...) __OS_HOOK_ ## NAME (__VA_ARGS__)

#endif
