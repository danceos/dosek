/**
 * @file
 * @ingroup unit_tests
 * @test Test the tasklist behaviour
 */

#include "test/test.h"
#include "../tasklist.h"

using namespace os::scheduler;

// errors are injected in this namespace
namespace fail {

// the task list
TaskList tlist;

// constant task identifiers
const Task t1(1,1);
const Task t2(2,2);
const Task t3(3,3);
const Task t4(4,4);

Encoded_Static<A0, 3> id;
Encoded_Static<A0, 2> prio;

// test a single dequeue
void test_dequeue() {
	tlist.dequeue(id, prio);
}

};

using namespace fail;

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

/**
 * @brief Runs dequeue tests
 */
void test(void)
{
	//! @test Dequeue everything
    run_checkable_function(&test_dequeue, id, 4);
	run_checkable_function(&test_dequeue, id, 3);
	run_checkable_function(&test_dequeue, id, 2);
	run_checkable_function(&test_dequeue, id, 1);
	run_checkable_function(&test_dequeue, id, 0);
}

