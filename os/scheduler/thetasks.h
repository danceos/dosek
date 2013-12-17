// TODO: this file will be generated from the application configuration!
#include "task.h"
#ifndef THETASKS
#define THETASKS

using os::scheduler::Task;


namespace os {
namespace tasks {

// task handlers
extern void start_Handler11(void);
extern void start_Handler12(void);
extern void start_Handler13(void);
extern void start_Handler14(void);

// the tasks
const Task t1(1, 2, start_Handler11);
const Task t2(2, 3, start_Handler12);
const Task t3(3, 1, start_Handler13);
const Task t4(4, 4, start_Handler14);

}; // namespace tasks
}; // namespace os

using namespace os::tasks;

#endif
