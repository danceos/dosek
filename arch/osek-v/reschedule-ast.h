/**
 * @file
 * @ingroup posix
 * @brief Posix reschedule AST interface
 */

#ifndef __RESCHEDULE_AST_H__
#define __RESCHEDULE_AST_H__

#include "os/util/inline.h"
#include "interrupt.h"


namespace arch {

 /** \brief Request the reschedule AST to run after all other interrupts compelete. */
 void request_reschedule_ast();

} // namespace arch

#endif // __RESCHEDULE_AST_H__
