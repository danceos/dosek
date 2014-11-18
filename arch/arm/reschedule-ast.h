/**
 * @file
 * @ingroup i386
 * @brief i386 reschedule AST interface
 */

#ifndef __RESCHEDULE_AST_H__
#define __RESCHEDULE_AST_H__

#include "os/util/inline.h"
#include "gic.h"

namespace arch {

/** \brief Request the reschedule AST to run after all other interrupts compelete. */
forceinline void request_reschedule_ast() {
    // reset save_sp to detect IRQ from non-userspace in idt.S
    //save_sp = 0;

	GIC::trigger(IRQ_RESCHEDULE);
}

} // namespace arch

#endif // __RESCHEDULE_AST_H__
