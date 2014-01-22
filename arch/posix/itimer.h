/**
 * @file
 * @ingroup posix
 * @brief POSIX Timer implementation
 */

#ifndef ITIMER_H_
#define ITIMER_H_

#include "stdint.h"

namespace arch {

/** \brief Posix timer */
class ITimer {

public:
	/** \brief Initialize the Timer */
	static void init(void);

	/** \brief Generate periodic 'interrupt' (signal) at given rate (in Hz) */
	static void set_periodic(uint16_t rate);
};

}; // namespace arch

#endif /* ITIMER_H_ */
