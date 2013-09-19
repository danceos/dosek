#include "output.h"
#include "tasklist.h"

output_t kout;

extern "C" {

// globals
char experiment_number = 0;
char detected_error = false;
char result = -1;
uint32_t& encoded_result = TaskList::id.vc;

TaskList tlist;

// markers
void _subexperiment_end() { };
void (*subexperiment_end)() = _subexperiment_end;

void _subexperiment_marker_1() { };
void (*subexperiment_marker_1)() = _subexperiment_marker_1;

void _trace_start_marker() { };
void (*trace_start_marker)() = _trace_start_marker;

void _trace_end_marker() { };
void (*trace_end_marker)() = _trace_end_marker;

static const Task t1(1,1);
static const Task t2(2,2);
static const Task t3(3,3);
static const Task t4(4,4);


void setup() {
	start(tlist, t1);
	start(tlist, t2);
	start(tlist, t3);
	start(tlist, t4);

	if(DEBUG) tlist.print();
}

/* Tests */
void test_dequeue() {
	tlist.dequeue();

	subexperiment_marker_1();
	
	detected_error = !TaskList::id.check();
	result = TaskList::id.decode();
}

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
};

void os_main(void) {
	kout << "CoRedOS start" << endl;

	setup();

	trace_start_marker();

	experiment_number = 1;
	test1();
	subexperiment_end();

	kout << "CoRedOS halt" << endl;

	for(;;) {}
}

