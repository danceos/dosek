/** \brief Check saved stack and instruction pointers for odd parity
 * Ensured by highest bit
 */
#define PARITY_CHECKS 1

/** \brief Check saved IRQ context on stack using a XOR checksum */
#define CHECK_IRQ_CONTEXT 1

/** \brief Check saved task context on stack using a XOR checksum */
// unused if CHECK_IRQ_CONTEXT == 1
#define CHECK_TASK_CONTEXT 1

/** \brief Perform syscalls using sysenter insteaf of int */
#define SYSENTER_SYSCALL 1

/** \brief Perform syscall dispatching using sysexit instead of iret */
// unused if SYSENTER_SYSCALL == 1
#define SYSEXIT_SYSCALL 1

/** \brief Enable task dispatching using sysexit instead of iret */
#define SYSEXIT_DISPATCH 1
