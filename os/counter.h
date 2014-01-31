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

protected:
	volatile Ticks value;

public:
	const Ticks maxallowedvalue;
	const Ticks ticksperbase;
	const Ticks mincycle;

	constexpr Counter() : value(0), maxallowedvalue(0xFFFFFFFF), ticksperbase(10000), mincycle(1) {}

	Ticks getValue() const {
		return value;
	}

	forceinline void advanceCounter();

	static forceinline void tick() {
		// TODO: advance all generated counters
		counter0.advanceCounter();
	}
};

}; // namespace os

/* the following is defined here instead of counter.cc to allow full inlining */

#include "alarm.h"

namespace os {
    extern called_once void Alarm_checkCounter(Counter &counter);

forceinline void Counter::advanceCounter() {
	if(value == maxallowedvalue) {
		value = 0;
	} else {
		value++;
	}

	Alarm_checkCounter(*this);
}

} // namespace os

#endif // COUNTER_H_
