#ifndef __TASKLIST_H__
#define __TASKLIST_H__

#ifndef DEBUG
#define DEBUG 0
#endif

#include <stdint.h>
#include "assert.h"
#include "output.h"
#include "task.h"
#include "encoded.h"

// the one A we use for now
static const A_t A0 = 58659;

// encoded constant
#define EC(b, v) Encoded_Static<A0, b>(v)



/* Simpler array based task queue */
class TaskList {
	// encoded task priorities
	Encoded_Static<A0, 17> task1;
	Encoded_Static<A0, 16> task2;
	Encoded_Static<A0, 15> task3;
	Encoded_Static<A0, 14> task4;

public:
	// idle task id/priority
	static constexpr auto idle_id = EC(13,0);
	static constexpr auto idle_prio = EC(12,0);

	// static variable for id, prio paramters/results
	// as references given as parameters would be put on stack
	static Encoded_Static<A0, 3> id;
	static Encoded_Static<A0, 2> prio;

	TaskList() :
		task1(0, 0), 
		task2(0, 0),
		task3(0, 0),
		task4(0, 0) {}


	/** Set priority of task id to prio **/
	// returns an encoded 0 with the signature (B) of the modified task - prio.B
	template<typename T, typename S>
	inline value_coded_t set(const T id, const S prio) {
	//inline value_coded_t set() {
		//volatile value_coded_t signature;
		if(id == 1) {
			task1 = prio;
			return (task1 - prio).getCodedValue();
		} else if(id == 2) {
			task2 = prio;
			return (task2 - prio).getCodedValue();
		} else if(id == 3) {
			task3 = prio;
			return (task3 - prio).getCodedValue();
		} else if(id == 4) {
			task4 = prio;
			return (task4 - prio).getCodedValue();
		} else {
			assert(false);
			return 0;
		}
	}

	// Effect: (a,x) = max{((a,x), (b,y)} with (a,x) <= (b,y) <=> a <= b
	// subtracts signature B0 from a,x and adds signature B1 to catch lost updates
	template<B_t B0, B_t B1, typename T, typename S, typename U, typename V>
	inline value_coded_t updateMax(T& a, const S& b, U& x, const V& y) const {
		TAssert(S::B > T::B);

		// control flow signature
		value_coded_t result;

		// check correct a,x after subtracting signature B0
		assert((a.vc - B0 - T::B - a.D) % T::A == 0);
		assert((x.vc - B0 - U::B - x.D) % U::A == 0);

		// unencoded comparison
		result = ((a.vc - B0) - T::B) <= (b.vc - S::B);
		
		// encoded check of comparison
		value_coded_t diff = b.vc - (a.vc - B0); // this>t  => diff = 2^m - (vc - t.vc)
						// this<=t => diff = t.vc - vc
		value_coded_t sigCond = diff % T::A;
		const value_coded_t sigPos = S::B - T::B;
		const value_coded_t sigNeg = (T::MAXMODA + sigPos) % T::A;

		if(result) {
			if(DEBUG) kout << "< ";

			// a=b, x=y with added signature B1
			a.vc = b.vc + (T::B - S::B) + B1;
			x.vc = y.vc + (U::B - V::B) + B1;

			// set control flow signature (expected: sigCond == sigPos)
			result += (T::A - 1) + B1; // + (S::B - T::B);
		} else {
			if(DEBUG) kout << "> ";

			// remove old B-1, add new B signature to "unmodified" a,x
			a.vc = a.vc - B0 + B1;
			x.vc = x.vc - B0 + B1;

			// set control flow signature (expected: sigCond == sigNeg)
			result += (sigPos - sigNeg) + B1; // + (S::B - T::B);
		}

		// return finished control flow signature
		result += sigCond;
		return result;
	}

	/** Get highest-priority task.
	  * Saves result ID in TaskList::id,
	  * and result priority in TaskList::prio.
	  * If no task is ready, TaskList::prio == TaskList::idle_prio
	  * and TaskList::id is undefined.
	  */
	//template<typename T, typename S>
	//inline value_coded_t head(T& id, S& prio) const {
	inline value_coded_t head() const {
		// initialize control flow signature
		volatile value_coded_t signature = 10;

		// start with idle id/priority
		id = idle_id;
		prio = idle_prio;

		// add initial signature
		id.vc += 10;
		prio.vc += 10;

		// task1 > prio?
		signature += updateMax<10, 11>(prio, task1, id, EC(41, 1));
		assert(signature % A0 == 36);

		// task2 > prio?
		signature += updateMax<11, 12>(prio, task2, id, EC(42, 2));
		assert(signature % A0 == 62);

		// task3 > prio?
		signature += updateMax<12, 13>(prio, task3, id, EC(43, 3));
		assert(signature % A0 == 88);

		// task4 > prio?
		signature += updateMax<13, 14>(prio, task4, id, EC(44, 4));
		assert(signature % A0 == 114);

		// subtract last signature
		id.vc -= 14;
		prio.vc -= 14;

		// check signatures
		assert(id.check());
		assert(prio.check());

		if(DEBUG) kout << "head: " << id.decode() << " (prio " << prio.decode() << ")" << endl;

		return signature;
	}

	template<typename T, typename S>
	inline value_coded_t insert(const T& id, const S& prio) {
		if(DEBUG) kout << "+++ Task " << id.decode() << " with priority " << prio.decode() << " is ready" << endl;

		return set(id, prio);
	}

	//template<typename T>
	//inline value_coeded_t remove(const T& id) {
	inline value_coded_t remove() {
		if(DEBUG) kout << "--- Task " << id.decode() << " removed from task queue" << endl;

		return set(id, EC(5, 0));
	}

	template<typename T, typename S>
	inline void promote(const T& id, const S& newprio) {
		if(DEBUG) kout << "^^^ Promoting task " << id.decode() << " to priority " << newprio.decode() << endl;
		
		set(id, newprio);
	}

	inline value_coded_t dequeue() {
		value_coded_t sig1 = head();

		value_coded_t sig2;
		if(prio != idle_prio) {
			sig2 = remove();
		} else {
			id = idle_id;
			sig2 = 42;
		}

		// TODO: check control flow
		// assert(...)
		/*
		Encoded_Static<A0, 13> i1;
		Encoded_Static<A0, 12> i2;
		Encoded_Static<A0, 11> i3;
		Encoded_Static<A0, 10> i4;
		switch(id.decode()) {
			case 1:
				i1.setCodedValue(sig2);
				assert(i1 == 0);
				return (i1 == 0);

			case 2:
				i2.setCodedValue(sig2);
				assert(i2 == 0);
				return (i2 == 0);

			case 3:
				i3.setCodedValue(sig2);
				assert(i3 == 0);
				return (i3 == 0);

			case 4:
				i4.setCodedValue(sig2);
				assert(i4 == 0);
				return (i4 == 0);

			default:
				assert(false);
				return false;
		}
		*/

		return sig1+sig2;
	}
	
	// DEBUGGING
	void print() const {
		kout << "(" << task1.decode() << "), ";
		kout << "(" << task2.decode() << "), ";
		kout << "(" << task3.decode() << "), ";
		kout << "(" << task4.decode() << ")" << endl;
	}
};

/*
bool start(TaskList &tl, const Task &t) {
	value_coded_t res = tl.insert(EC(3, t.getID()), EC(4, t.getPrio()));

	Encoded_Static<A0, 13> i1;
	Encoded_Static<A0, 12> i2;
	Encoded_Static<A0, 11> i3;
	Encoded_Static<A0, 10> i4;
	switch(t.getID()) {
		case 1:
			i1.setCodedValue(res);
			assert(i1 == 0);
			return (i1 == 0);

		case 2:
			i2.setCodedValue(res);
			assert(i2 == 0);
			return (i2 == 0);

		case 3:
			i3.setCodedValue(res);
			assert(i3 == 0);
			return (i3 == 0);

		case 4:
			i4.setCodedValue(res);
			assert(i4 == 0);
			return (i4 == 0);

		default:
			assert(false);
			return false;
	}
}
*/

#endif // __TASKLIST_H__
