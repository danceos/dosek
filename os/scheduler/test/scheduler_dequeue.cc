//#define DEBUG 1

#include "test/test.h"
#include "../tasklist.h"

extern "C" {

// the task list
TaskList tlist;

// constant task identifiers
static const Task t1(1,1);
static const Task t2(2,2);
static const Task t3(3,3);
static const Task t4(4,4);

Encoded_Static<A0, 3> id;
Encoded_Static<A0, 2> prio;

// test a single dequeue
void test_dequeue() {
	tlist.dequeue(id, prio);
}

// prepare tests
void test_prepare(void)
{
	// start all tasks
	tlist.insert(EC(3, t1.getID()), EC(4, t1.getPrio()));
	tlist.insert(EC(3, t2.getID()), EC(4, t2.getPrio()));
	tlist.insert(EC(3, t3.getID()), EC(4, t3.getPrio()));
	tlist.insert(EC(3, t4.getID()), EC(4, t4.getPrio()));

	if(DEBUG) tlist.print();
}

// run tests
void test(void)
{
	// dequeue everything
	run_checkable_function(&test_dequeue, id, 4);
	run_checkable_function(&test_dequeue, id, 3);
	run_checkable_function(&test_dequeue, id, 2);
	run_checkable_function(&test_dequeue, id, 1);
	run_checkable_function(&test_dequeue, id, 0);
}

};
