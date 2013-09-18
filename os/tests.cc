#include "scheduler.cc" // FIXME

extern "C" {

TaskList tlist;

const Task t1(1,1);
const Task t2(2,2);
const Task t3(3,3);
const Task t4(4,4);


void setup() {
	start(tlist, t1);
	start(tlist, t2);
	start(tlist, t3);
	start(tlist, t4);

	if(DEBUG) tlist.print();
}

Encoded_Static<A0, 3> next;
Encoded_Static<A0, 2> prio;

uint32_t& encoded_result = next.vc;
char result = -1;
char detected_error = false;

/* Tests */
void test1() {
	tlist.dequeue(next, prio);
	
	detected_error = !next.check();
	result = next.decode();
}

};

/*
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

	bool right = true;

	right &= ( schedule(tlist) == 2 );
	right &= ( schedule(tlist) == 3 );
	right &= ( schedule(tlist) == 0 );
	right &= ( schedule(tlist) == 0 );

	return right;
}
	
// Arithmetic tests
bool test_arith() {
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
*/

