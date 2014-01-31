#ifndef COUNTER_H_
#define COUNTER_H_

#include "stdint.h"
#include "util/inline.h"

namespace os {

class Counter;
extern Counter counter0;

/** OSEK Counter
 *
 * Base timer initialized by arch/
 */
class Counter {
public:
	typedef uint32_t Ticks;


	volatile Ticks value;

	const Ticks maxallowedvalue;
	const Ticks ticksperbase;
	const Ticks mincycle;

	constexpr Counter() : value(0), maxallowedvalue(0xFFFFFFFF), ticksperbase(10000), mincycle(1) {}
	constexpr Counter(Ticks mav, Ticks tpb, Ticks mc) : value(0), maxallowedvalue(mav), ticksperbase(tpb), mincycle(mc) {}

	Ticks getValue() const {
		return value;
	}

	static void tick();
};


}; // namespace os



#endif // COUNTER_H_
