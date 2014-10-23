/**
 * @file
 * @ingroup arm
 * @brief ARM Private Timer
 */

#ifndef TIMER_H_
#define TIMER_H_

#include "stdint.h"
#include "platform.h"

namespace arch {

/** \brief Private Timer */
class Timer {
	enum {
        PRESCALEMASK = 0x0000FF00, //!< Prescaler Mask
        PRESCALESHIFT = 8, //!< Shift width for prescale value
	};

    typedef struct PRV_TIMER_regs {
        uint32_t load;
        uint32_t counter;
        uint32_t control;
        uint32_t isr_status;
    } PRV_Timer_regs;

    static volatile PRV_Timer_regs * const timer;

public:
   	/** \brief Initialize the Timer */
	static void init();

	/** \brief Generate periodic interrupt at given rate (in Hz) */
	static void set_periodic(uint16_t rate);

	/** \brief Acknowldge interrupt in ISR */
    static void ack_isr(void) {
        timer->isr_status = 1;
    }
};

}; // namespace arch


#endif /* TIMER_H_ */
