#ifndef COUNTER_H_
#define COUNTER_H_

#include "stdint.h"
#include "util/inline.h"
#include "os.h"

#include "util/encoded.h"

namespace os {

/** OSEK Counter
 *
 * Base timer initialized by arch/
 */
class Counter {
public:
	inlinehint static void tick();
};

class UnencodedCounter : public Counter {
public:
	typedef uint16_t Ticks; // TODO: uint32?
	volatile Ticks value;

	const Ticks maxallowedvalue;
	const Ticks ticksperbase;
	const Ticks mincycle;

	constexpr UnencodedCounter() : value(0), maxallowedvalue(0xFFFF), ticksperbase(10000), mincycle(1) {}
	constexpr UnencodedCounter(TickType mav, TickType tpb, TickType mc) : value(0), maxallowedvalue(mav), ticksperbase(tpb), mincycle(mc) {}

	forceinline Ticks getValue() const {
		return value;
	}

	forceinline void do_tick() {
		if(getValue() == maxallowedvalue) {
			value = 0;
		} else {
			value += 1;
		}
	}
};

template<B_t B>
class EncodedCounter : public Counter {
public:
	typedef Encoded_Static<A0, B> value_t;
	volatile value_t value;

	const Encoded_Static<A0, B+1> maxallowedvalue;
	const Encoded_Static<A0, B+2> ticksperbase;
	const Encoded_Static<A0, B+3> mincycle;

	constexpr EncodedCounter() : value(0), maxallowedvalue(0xFFFF), ticksperbase(10000), mincycle(1) {}
	constexpr EncodedCounter(TickType mav, TickType tpb, TickType mc) : value(0), maxallowedvalue(mav), ticksperbase(tpb), mincycle(mc) {}

	forceinline value_t getValue() const {
		value_t res;
		assert(value.check());
		res.vc = value.vc;
		return res;
	}

	forceinline void do_tick() {
		if(getValue() == maxallowedvalue) {
			value = EC(B+4, 0);
		} else {
			value += EC(B+5, 1);
		}
	}
};

}; // namespace os

#endif // COUNTER_H_
