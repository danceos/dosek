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

int a;

extern "C" void bar() {
	ActivateTask(Handler13);
}

extern "C" void foo() {
	a++;
	return;
}




TASK(Handler11) {
	a++;
	if (a == 12) {
		ActivateTask(Handler12);
	}

	if (a == 100) {
		bar();
		a++;
	} else {
		foo();
		ActivateTask(Handler13);
	}
	TerminateTask();
}

TASK(Handler12) {
	TerminateTask();
}

TASK(Handler13) {
	TerminateTask();
}

