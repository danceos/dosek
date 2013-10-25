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

// encoded argument/result variables
Encoded_Static<A0, 3> id;
Encoded_Static<A0, 2> prio;

// return value for calls
value_coded_t returnvalue;

// test a single dequeue
void test_dequeue() {
	tlist.dequeue(id, prio);
}

// test a single promote
template <int ID, int NEWPRIO> void test_promote() {
	returnvalue = tlist.promote(EC(3, ID), EC(4, NEWPRIO));
}

// test a single remove
template <int ID> void test_remove() {
	returnvalue = tlist.remove(EC(3, ID));
}

// test a single start
template <int ID, int PRIO=ID> void test_start() {
	returnvalue = tlist.insert(EC(3, ID), EC(4, PRIO));
}

};

using namespace fail;

// prepare tests
void test_prepare(void)
{
	// start all tasks
	test_start<1>();
	test_start<2>();
	test_start<3>();
	test_start<4>();

	if(DEBUG) tlist.print();
}

/**
 * @brief Runs tasklist tests
 */
void test(void)
{
	//! @test Remove and dequeue one task
	run_checkable_function(&test_remove<4>, returnvalue, 9, true);
	run_checkable_function(&test_dequeue, id, 3);
	run_checkable_function(&test_remove<2>, returnvalue, 11, true);
	run_checkable_function(&test_dequeue, id, 1);

	//! @test Remove+dequeue on empty list
	run_checkable_function(&test_remove<4>, returnvalue, 9, true);
	run_checkable_function(&test_dequeue, id, 0);
	run_checkable_function(&test_remove<2>, returnvalue, 11, true);
	run_checkable_function(&test_dequeue, id, 0);

	//! @test Start tasks 1..3, promote 1,2, dequeue them
	run_checkable_function(&test_start<1>, returnvalue, 13, true);
	run_checkable_function(&test_start<2>, returnvalue, 12, true);
	run_checkable_function(&test_start<3>, returnvalue, 11, true);
	run_checkable_function(&test_promote<2,4>, returnvalue, 12, true);
	run_checkable_function(&test_dequeue, id, 2);
	run_checkable_function(&test_promote<1,4>, returnvalue, 13, true);
	run_checkable_function(&test_dequeue, id, 1); // SDC ret
	run_checkable_function(&test_dequeue, id, 3);

	//! @test Dequeue on empty list
	run_checkable_function(&test_dequeue, id, 0);
	run_checkable_function(&test_dequeue, id, 0);

	//! @test Start and dequeue one task
	run_checkable_function(&test_start<1>, returnvalue, 13, true);
	run_checkable_function(&test_dequeue, id, 1);
	run_checkable_function(&test_start<2>, returnvalue, 12, true);
	run_checkable_function(&test_dequeue, id, 2);
	run_checkable_function(&test_start<3>, returnvalue, 11, true);
	run_checkable_function(&test_dequeue, id, 3);
	run_checkable_function(&test_start<4>, returnvalue, 10, true);
	run_checkable_function(&test_dequeue, id, 4);

	//! @test Start all tasks
	run_checkable_function(&test_start<1>, returnvalue, 13, true);
	run_checkable_function(&test_start<2>, returnvalue, 12, true);
	run_checkable_function(&test_start<3>, returnvalue, 11, true);
	run_checkable_function(&test_start<4>, returnvalue, 10, true);

	//! @test Dequeue all tasks
	run_checkable_function(&test_dequeue, id, 4);
	run_checkable_function(&test_dequeue, id, 3);
	run_checkable_function(&test_dequeue, id, 2);
	run_checkable_function(&test_dequeue, id, 1);

	//! @test Dequeue empty list
	run_checkable_function(&test_dequeue, id, 0);
	run_checkable_function(&test_dequeue, id, 0);
}

