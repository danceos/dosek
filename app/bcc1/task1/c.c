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

void bar() {
	ActivateTask(Handler12);
}

void foo() {
	a++;
	return;
}




TASK(Handler11) {
	a++;
	if (a == 100) {
		bar();
		a++;
	} else {
		foo();
	}
	ChainTask(Handler13);
}

TASK(Handler12) {
	TerminateTask();
}

TASK(Handler13) {
	TerminateTask();
}
