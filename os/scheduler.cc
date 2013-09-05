//#include <stdio.h>
#include <stdint.h>
//#include <assert.h>
#include "Assert.h"

#define assert(...) do {} while(0)
//#define assert(x) (void)(((x)==0)? printf("ASSERT %s (%s:%u %s)\n", #x,__FILE__,__LINE__,__func__):0)

#include "Encoded.h"

#define printf(...) do {} while(0)
// the one A we use for now
static const A_t A0 = 58659;

// encoded constant
#define EC(b, v) Encoded_Static<A0, b>(v)



/* Simple task class */
class Task {
public:
	typedef uint8_t ID;
	typedef uint8_t Prio;

protected:
	union {
		struct {
			ID id;
			Prio prio;

		} fields;
		uint16_t combined;
	};

public:
	Task() : combined(0) {}

	Task(uint16_t comb) : combined(comb) {};

	Task(ID tid, Prio p) {
		fields.id = tid;
		fields.prio = p;
	} 

	ID getID() const {
		return fields.id;
	}

	Prio getPrio() const {
		return fields.prio;
	}

	uint16_t getCombined() const {
		return combined;
	}

	void setPrio(Prio newprio) {
		fields.prio = newprio;
	}
};

typedef Task::ID TaskID;
typedef Task::Prio TaskPrio;
static const Task INVALID_TASK = Task(0,0);
static const TaskID INVALID_TASK_ID = 0;



/* Binary tree based task queue */
class TaskTree {
	Encoded_Static<A0, 17> task1;
	Encoded_Static<A0, 16> task2;
	Encoded_Static<A0, 15> task3;
	Encoded_Static<A0, 14> task4;

	Encoded_Static<A0, 13> task12;
	Encoded_Static<A0, 12> task34;

	Encoded_Static<A0, 11> task1234;

	const value_coded_t signatures[5] = {
		42, // no task
		(value_coded_t) (task12.getB() - task1234.getB()) + (task1.getB() - task1234.getB()),
		(value_coded_t) (task12.getB() - task1234.getB()) + (task2.getB() - task1234.getB()),
		(value_coded_t) (task34.getB() - task1234.getB()) + (task3.getB() - task1234.getB()),
		(value_coded_t) (task34.getB() - task1234.getB()) + (task4.getB() - task1234.getB()),
	};

public:
	TaskTree() :
		task1(0, 0), 
		task2(0, 0),
		task3(0, 0),
		task4(0, 0),
		task12(0, 0),
		task34(0, 0),
		task1234(0, 0) {}

	// TODO: good idea? unencoded result!
	bool isEmpty() {
		return task1234 == 0;
	}

	/*
	template<typename T, typename S>
	void set(T id, S prio) {
        volatile value_coded_t signature;

		if(id == 1) {
			task1 = prio;

			if(task1 >= task2) {
				task12 = task1;
			} else {
				task12 = task2;
			}
		} else if(id == 2) {
			task2 = prio;

			if(task1 >= task2) {
				task12 = task1;
			} else {
				task12 = task2;
			}
		} else if(id == 3) {
			task3 = prio;

			if(task3 >= task4) {
				task34 = task3;
			} else {
				task34 = task4;
			}
		} else if(id == 4) {
			task4 = prio;

			if(task3 >= task4) {
				task34 = task3;
			} else {
				task34 = task4;
			}
		} else {
			assert(false);
		}

		if(task12 >= task34) {
			task1234 = task12;
		} else {
			task1234 = task34;;
		}
	}
	*/

	template<typename T, typename S>
	void set(T id, S prio) {
        volatile value_coded_t signature;

        auto one = Encoded_Static<A0, 42>(1);

		if(id == 1) {
			task1 = prio;

			auto leq21 = task2 <= task1;
			task12 = task1 * leq21 + task2 * (one - leq21); 
		} else if(id == 2) {
			task2 = prio;

			auto leq21 = task2 <= task1;
			task12 = task1 * leq21 + task2 * (one - leq21); 
		} else if(id == 3) {
			task3 = prio;

			auto leq34 = task4 <= task3;
			task34 = task3 * leq34 + task4 * (one - leq34); 
		} else if(id == 4) {
			task4 = prio;

			auto leq34 = task4 <= task3;
			task34 = task3 * leq34 + task4 * (one - leq34); 
		} else {
			assert(false);
		}

		auto leq1234 = task34 <= task12;
		task1234 =  task12 * leq1234 + task34 * (one - leq1234);
	}

	template<typename T, typename S>
	value_coded_t head(T& id, S& prio) {
        volatile value_coded_t signature;

		if(isEmpty()) { // TODO: good idea?
			signature = signatures[0];
			return signature;
		}

		if(task1234 == task12) {
			if(task1234 == task1) {
				signature = (task12.getCodedValue() - task1234.getCodedValue()) + (task1.getCodedValue() - task1234.getCodedValue());
				//id.encode(1, id.getD()); // additional redundancy by signature
				id = Encoded_Static<A0, 51>(1);
				prio = task1;
				return signature;
			} else if(task1234 == task2) {
				signature = (task12.getCodedValue() - task1234.getCodedValue()) + (task2.getCodedValue() - task1234.getCodedValue());
				//id.encode(2, id.getD()); // additional redundancy by signature
				id = Encoded_Static<A0, 52>(2);
				prio = task2;
				return signature;
			}
		} else if(task1234 == task34) {
			if(task1234 == task3) {
				signature = (task34.getCodedValue() - task1234.getCodedValue()) + (task3.getCodedValue() - task1234.getCodedValue());
				//id.encode(3, id.getD()); // additional redundancy by signature
				id = Encoded_Static<A0, 53>(3);
				prio = task3;
				return signature;
			} else if(task1234 == task4) {
				signature = (task34.getCodedValue() - task1234.getCodedValue()) + (task4.getCodedValue() - task1234.getCodedValue());
				//id.encode(4, id.getD()); // additional redundancy by signature
				id = Encoded_Static<A0, 54>(4);
				prio = task4;
				return signature;
			}
		}

		assert(false);
	}

	template<typename T, typename S>
	void insert(T id, S prio) {
		printf("+++ Task %d with priority %d is ready\n", id.decode(), prio.decode());

		set(id, prio);
	}

	template<typename T>
	void remove(T id) {
		if(isEmpty()) return;

		Encoded_Static<A0, 5> prio;
		prio.encode(0, 0);
		set(id, prio);
	}

	template<typename T, typename S>
	void promote(T&id, S& newprio) {
		printf("^^^ Promoting task %d to priority %d\n", id.decode(), newprio.decode());
		
		set(id, newprio);
	}

	template<typename T, typename S>
	bool dequeue(T& id, S& prio) {
		if(isEmpty()) return false;

		value_coded_t sig = head(id, prio);

		remove(id);

		printf("%u - %u - %u mod= %u" , id.getCodedValue(), id.getB(), id.getD(),
			(id.getCodedValue() - id.getB() - id.getD()) / id.getA());
		if(sig != TaskTree::signatures[id.decode()]) {
			assert(false);
		}
		
		return true;
	}

	
	// DEBUGGING
	void print() const {
		Task t1234 = Task(task1234.decode());
		Task t12 = Task(task12.decode());
		Task t34 = Task(task34.decode());
		Task t1 = Task(task1.decode());
		Task t2 = Task(task2.decode());
		Task t3 = Task(task3.decode());
		Task t4 = Task(task4.decode());

		printf("          (%d,%d)\n",  t1234.getID(), t1234.getPrio());
		printf("         /    \\\n");
		printf("  (%d, %d)       (%d, %d)\n", t12.getID(), t12.getPrio(), t34.getID(), t34.getPrio());
		printf(" /      \\      /    \\\n");
		printf("(%d,%d) (%d,%d)  (%d,%d) (%d,%d)\n", t1.getID(), t1.getPrio(), t2.getID(), t2.getPrio(), t3.getID(), t3.getPrio(), t4.getID(), t4.getPrio());
	}
};

/**************************************************/


/* Simpler array based task queue */
class TaskList {
	Encoded_Static<A0, 17> task1;
	Encoded_Static<A0, 16> task2;
	Encoded_Static<A0, 15> task3;
	Encoded_Static<A0, 14> task4;

	Encoded_Static<A0, 13> idle_id;
	Encoded_Static<A0, 12> idle_prio;

public:
	TaskList() :
		task1(0, 0), 
		task2(0, 0),
		task3(0, 0),
		task4(0, 0),
		idle_id(0, 0),
		idle_prio(0, 0) {}

	template<typename T, typename S>
	value_coded_t set(const T id, const S prio) {
        volatile value_coded_t signature;
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
		}
	}

	/*
	template<typename T, typename S>
	value_coded_t head(T& id, S& prio) {
        volatile value_coded_t signature;

        auto one = Encoded_Static<A0, 42>(1);

        id = idle_id;
        prio = idle_prio;

		auto leq01 = prio <= task1;
		prio = task1 * leq01 + prio * (one - leq01);
		id = Encoded_Static<A0, 51>(1) * leq01 + id * (one - leq01);
		//task1.D++;

		auto leq21 = prio <= task2;
		prio = task2 * leq21 + prio * (one - leq21);
		id = Encoded_Static<A0, 52>(2)  * leq21 + id * (one - leq21);
		//task2.D++;

		auto leq32 = prio <= task3;
		prio = task3 * leq32 + prio * (one - leq32);
		id = Encoded_Static<A0, 53>(3) * leq32 + id * (one - leq32);
		//task3.D++;

		auto leq43 = prio <= task4;
		prio = task4 * leq43 + prio * (one - leq43);
		id = Encoded_Static<A0, 54>(4) * leq43 + id * (one - leq43);
		//task4.D++;

		//idle_id.D++;
		//idle_prio.D++;

        return signature;
	}
	*/

	// Effect: (a,x) = max((a,x), (b,y)) with (a,x) <= (b,y) <=> a <= b
	template<B_t B, typename T, typename S, typename U, typename V>
	value_coded_t updateMax(T& a, const S& b, U& x, const V& y) const {
		value_coded_t result;
        result = (a.vc - T::B) <= (b.vc - S::B);
        
        // encoded check of comparison
        value_coded_t diff = b.vc - a.vc; // this>t  => diff = 2^m - (vc - t.vc)
                                        // this<=t => diff = t.vc - vc
        value_coded_t sigCond = diff % T::A;
        const value_coded_t sigPos = S::B - T::B;
        const value_coded_t sigNeg = (T::MAXMODA + sigPos) % T::A;

        if(result) {
            // expected: sigCond == sigPos
        	a = b;
        	x = y;
            result += (T::A - 1) + (S::B - T::B) + B;
        } else {
            // expected: sigCond == sigNeg
            result += (sigPos - sigNeg) + (S::B - T::B) + B;
        }
        result += sigCond;
        return result;
	}

	template<typename T, typename S>
	value_coded_t head(T& id, S& prio) const {
        volatile value_coded_t signature = 10;

        id = idle_id;
        prio = idle_prio;

        volatile value_coded_t s1,s2,s3,s4;

        signature += updateMax<11>(prio, task1, id, EC(41, 1));
        assert(signature % T::A == 51);

        signature += updateMax<12>(prio, task2, id, EC(42, 2));
        assert(signature % T::A == 91);

        signature += updateMax<13>(prio, task3, id, EC(43, 3));
        assert(signature % T::A == 130);

        signature += updateMax<14>(prio, task4, id, EC(44, 4));
        assert(signature % T::A == 168);

        return signature;
	}

	template<typename T, typename S>
	value_coded_t insert(const T& id, const S& prio) {
		printf("+++ Task %d with priority %d is ready\n", id.decode(), prio.decode());

		return set(id, prio);
	}

	template<typename T>
	void remove(const T& id) {
		set(id, EC(5, 0));
	}

	template<typename T, typename S>
	void promote(const T& id, const S& newprio) {
		printf("^^^ Promoting task %d to priority %d\n", id.decode(), newprio.decode());
		
		set(id, newprio);
	}

	template<typename T, typename S>
	bool dequeue(T& id, S& prio) {
		value_coded_t sig = head(id, prio);

		remove(id);

		return true;
	}

	
	// DEBUGGING
	void print() const {
		printf("(%d), ", task1.decode());
		printf("(%d), ", task2.decode());
		printf("(%d), ", task3.decode());
		printf("(%d)\n", task4.decode());
	}
};



/* Test functions */
void dispatch(TaskID t) {
	printf(">>> Dispatching task %d\n", t);
}

TaskID schedule(TaskList &tl) {
	Encoded_Static<A0, 3> next;
	Encoded_Static<A0, 2> prio;

	tl.dequeue(next, prio);

	if((EC(1, 1) <= prio).decode()) {
		dispatch(next.decode());
		return next.decode();
	} else {
		printf("... Entering idle\n");
		return 0;
	}

}

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
			break;

		case 2:
			i2.setCodedValue(res);
			assert(i2 == 0);
			return (i2 == 0);
			break;

		case 3:
			i3.setCodedValue(res);
			assert(i3 == 0);
			return (i3 == 0);
			break;

		case 4:
			i4.setCodedValue(res);
			assert(i4 == 0);
			return (i4 == 0);
			break;
	}
}


TaskList tlist;

Task t1(1,1);
Task t2(2,2);
Task t3(3,3);
Task t4(4,4);

void setup() {
	start(tlist, t1);
	start(tlist, t2);
	start(tlist, t3);
	start(tlist, t4);

	tlist.print();
}

/* Tests */
bool test1() {
	//assert( schedule(tlist) == 4 );
	Encoded_Static<A0, 3> next;
	Encoded_Static<A0, 2> prio;

	tlist.dequeue(next, prio);
	printf("DEBUG %u\n", t1.getID());
	printf("%u == 4 : %u\n", next.decode(), next == 4);

	return (next == 4);
}
	
bool test2() {
	bool right = true;
	right &= ( schedule(tlist) == 3 );
	right &= ( schedule(tlist) == 2 );
	right &= ( schedule(tlist) == 1 );
	right &= ( schedule(tlist) == 0 );
	right &= ( schedule(tlist) == 0 );

	return right;
}

bool test3() {
	start(tlist, t3);
	start(tlist, t2);
	
	tlist.promote( EC(5, t2.getID()), EC(6, 4) );

	//tlist.print();
	bool right = true;

	right &= ( schedule(tlist) == 2 );
	//tlist.print();

	right &= ( schedule(tlist) == 3 );
	//tlist.print();

	right &= ( schedule(tlist) == 0 );
	right &= ( schedule(tlist) == 0 );


	return true; // TODO
}
	
bool test_arith() {
	/* Arithmetic tests */
	Encoded_Static<A0, 11> x(44 ,0);
	Encoded_Static<A0, 17> y(55, 0);
	Encoded_Static<A0, 1700> yb(5, 0);
	Encoded_Static<A0, 45> z(35, 0);

	assert( (z-x+y).decode() == 46 );
	assert( y.geqz() == 1 );
	assert( (z >= y) == 0 );
	assert( (y >= x) == 1 );
	assert( (x <= y) == 1 );
	assert( (x <= yb) == 0 );
	assert( x.leq<42>(yb) == 0 );
	assert( (y*x) == 2420 );

	return true;
}

