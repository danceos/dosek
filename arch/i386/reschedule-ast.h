/**
 * @file
 * @ingroup i386
 * @brief i386 reschedule AST interface
 */

#ifndef __RESCHEDULE_AST_H__
#define __RESCHEDULE_AST_H__

#include "os/util/inline.h"
#include "lapic.h"

namespace arch {

/** \brief Request the reschedule AST to run after all other interrupts compelete. */
forceinline void request_reschedule_ast() {
	LAPIC::trigger(IRQ_RESCHEDULE);
}

} // namespace arch

#endif // __RESCHEDULE_AST_H__