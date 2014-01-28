/**
 * @file
 * @ingroup i386
 * @brief i386 exception number constants
 */

#ifndef EXCEPTION_H_
#define EXCEPTION_H_

namespace arch {

enum Exceptions {
	DIV0 = 0,
	DBG,
	NMI,
	BREAKPOINT,
	OVERFLOW,
	BOUND_RANGE_EXCEEDED,
	INVALID_OPCODE,
	DEVICE_NOT_AVAILABLE,
	DOUBLE_FAULT, // error code
	COPROCESSOR_SEGMENT_OVERRUN,
	INVALID_TSS, // error code
	SEGMENT_NOT_PRESENT, // error code
	STACK_SEGMENT_FAULT, // error code
	GPF, // error code
	PAGE_FAULT, // error code
	X87_FP_EXCEPTION = 16,
	ALIGNMENT_CHECK, // error code
	MACHINE_CHECK,
	SIMD_FP_EXCEPTION,
	SECURITY_EXCEPTION = 30
};

}

#endif /* EXCEPTION_H_ */
