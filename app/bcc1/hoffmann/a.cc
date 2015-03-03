/**
 * @defgroup apps Applications
 * @brief The applications...
 */

/**
 * @file
 * @ingroup apps
 * @brief Just a simple test application
 */
#include "os.h"


DeclareTask(Handler11);
DeclareTask(Handler12);
DeclareTask(Handler13);

void os_main(void) { StartOS(0); }

volatile int foo;

void haha12(void) {
    if (foo > 42) {
	    ActivateTask(Handler12);
    }
}

void ha12(void) {
    haha12();
}

void haha13(void) {
	ActivateTask(Handler13);
}

void ha13(void) {
    haha13();
}

TASK(Handler11) {
	ha12();
        ha13();
	TerminateTask();
}

/********* Task 12 ******/
TASK(Handler12) {
	TerminateTask();
}

/********* Task 13 ******/
void test___a___(void) {

}

void test___b___(void) {

}

void test___c___(void) {

}

//
//void test___d1__(void) {
//
//}

void test___d___(void) {
    //test___d1__();
}



TASK(Handler13) {
        test___a___();
        test___b___();
        test___c___();
        test___d___();
	TerminateTask();
}

/****** EOT Task 13 ******/

void PreIdleHook() {
	ShutdownMachine();
}
