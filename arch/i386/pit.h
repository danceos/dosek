/**
 * @file
 * @ingroup i386
 * @brief i386 Programmable Interval Timer (PIT)
 */

#ifndef PIT_H_
#define PIT_H_

#include "stdint.h"

namespace arch {

/** \brief Programmable Interval Timer (PIT) */
class PIT {
	enum {
		PIT_RATE = 1193180, //!< base tick rate in Hz
		PIT_CHANNEL0_PORT = 0x40, //!< channel 0 IO port
		PIT_COMMAND_PORT = 0x43 //!< PIT command port
	};

public:
	/** \brief Initialize the PIT */
	static void init();

	/** \brief Generate periodic interrupt at given rate (in Hz) */
	static void set_periodic(uint16_t rate);
};

}; // namespace arch

#endif /* PIT_H_ */
