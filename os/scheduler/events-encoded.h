#include "os/util/encoded.h"
#include "os/scheduler/tasklist.h"


template<int B0 = 3, int B1 = 7, int High = 1>
class Event {
	Encoded_Static<A0, B0> event_waiting;
	Encoded_Static<A0, B1> event_set;

	static_assert(B1 > B0, "static signature B1 must be > B0");

public:
	Event() : event_waiting(0), event_set(0) {}


    /*
      Values H(high), L(ow)=0
      State: W(aiting) / S(et)

                     Wait-for-Event    No-Wait

    Event-Cleared    H / L              L / L
    Event-Set        H / H              L / H

    set() { S = H; }
    clear() { W = L; S = L; }
    is_blocked() -> H==No Influence | L==Should Unblock {

       return   ( (W ^ S) | ( S ^ H) )
       H    H      H   L  |   H   H
       L    H      L   H  |   L   L

    }

    is_waiting() -> H=Should Wait | L == No influcen {
        return W;
    }

     */

	/*
	   This function can only be called by the task itself, therefore
	   it resets the waiting AND the set flags
	*/
	void clear() {
		event_waiting = EC(B0, 0);
		event_set = EC(B1, 0);
	}

	void set() {
		event_set = EC(B1, High);
	}

	bool get() {
		return (event_set.vc == EC(B1, High).vc);
	}

	void wait() {
		event_waiting = EC(B0, High);
	}

	void unwait() {
		event_waiting = EC(B1, 0);
	}

	/* This is blocked function, either returns EC(0, High) or 0
	   depending on the two flags variables. This is a branchless
	   version, please look at the transition diagram above to
	   understand what is happending here.
	*/
	value_coded_t  is_blocked() const {
		value_coded_t W = (event_waiting.vc - B0);
		value_coded_t S = (event_set.vc - B1);
		constexpr value_coded_t H = (High * A0);
		return  (W ^ S) | (S ^ H);
	}

	/*
	   Returns EC(0, High) (is waiting!) or EC(0, 0) (this event is
	   not waiting
	*/
	value_coded_t is_waiting() const {
		value_coded_t W = (event_waiting.vc - B0);
		return  W;
	}

	static Encoded_Static<A0, B0> must_wait_p() {
		return EC(B0, 0);
	}

	template<typename ...Types>
	static Encoded_Static<A0, B0> must_wait_p(Types ...args) {
		Encoded_Static<A0, B0> ret;
		value_coded_t waiting = combine_waiting(args...);
		value_coded_t blocked = combine_blocked(args...);
		ret.vc = (waiting & blocked) + B0;
		return ret;
	}

private:

	/* This is a variadic template to combine the blocking state of
	   several event. If one event exposes L we will return L. We will
	   AND the is_blocked() of all arguments. */
	template<typename Ev>
	static value_coded_t combine_waiting(Ev event) {
		return event.is_waiting();
	}
	template<typename Ev, typename... Types>
	static value_coded_t combine_waiting(Ev event, Types... args) {
		return event.is_waiting() | combine_waiting(args...);
	}


	/* This is a variadic template to combine the waiting state of
		   several event. If one event should wait we return  return H. We will
		   OR the is_waiting() of all arguments. */
	template<typename Ev>
	static value_coded_t combine_blocked(Ev event) {
		return event.is_blocked();
	}
	template<typename Ev, typename... Types>
	static value_coded_t combine_blocked(Ev event, Types... args) {
		return event.is_blocked() & combine_blocked(args...);
	}
};

#if 0
Event<3, 7, 1> event_a;
Event<4, 9, 1> event_b;

int main() {

	event_a.wait();
	//event_b.wait();
	event_a.set();
	event_b.clear();


	auto ret = Event<12>::must_wait_p(event_a, event_b);

	std::cout << (ret.vc == (A0 + 12) ? "waiting" : "not-waiting" ) << std::endl;



	return 0;
}
#endif
