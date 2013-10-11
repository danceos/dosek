#include "os.h"

DeclareTask(Handler11);
DeclareTask(Handler12);
DeclareTask(Handler13);

TASK(Handler11) {
  unsigned int a = 0;

  a++;
  a++;


  ActivateTask(Handler12);

  a++;
  a++;

  ActivateTask(Handler13);

  a++;
  a++;

  TerminateTask();
}

TASK(Handler12) {
  unsigned int a = 0;

  a++;
  a++;
  a++;

  TerminateTask();
}

TASK(Handler13) {
  unsigned int a = 0;

  a++;
  a++;
  a++;

  TerminateTask();
}
