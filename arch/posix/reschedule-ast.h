/**
 * @file
 * @ingroup posix
 * @brief Posix reschedule AST interface
 */

#ifndef __RESCHEDULE_AST_H__
#define __RESCHEDULE_AST_H__

#include "os/util/inline.h"
#include "irq.h"


namespace arch {

/** \brief Request the reschedule AST to run after all other interrupts compelete. */
forceinline void request_reschedule_ast() {
	irq.request_ast();
    return;
}

} // namespace arch

#endif // __RESCHEDULE_AST_H__
