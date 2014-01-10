// TODO: this file will be generated from the application configuration!

#include "task.h"
#ifndef THETASKS
#define THETASKS

using os::scheduler::Task;

// task handlers
extern "C" __attribute__((weak_import)) void Task1_function(void);
extern "C" __attribute__((weak_import)) void Task2_function(void);
extern "C" __attribute__((weak_import)) void Task3_function(void);
extern "C" __attribute__((weak_import)) void Task4_function(void);

// task stacks
extern "C" uint8_t Task1_stack[];
extern "C" uint8_t Task2_stack[];
extern "C" uint8_t Task3_stack[];
extern "C" uint8_t Task4_stack[];

// task stack pointers
extern "C" void* stackptr_Task1;
extern "C" void* stackptr_Task2;
extern "C" void* stackptr_Task3;
extern "C" void* stackptr_Task4;

namespace os {
namespace tasks {

// the tasks
constexpr Task t1(1, 2, Task1_function, &Task1_stack, stackptr_Task1);
constexpr Task t2(2, 3, Task2_function, &Task2_stack, stackptr_Task2);
constexpr Task t3(3, 1, Task3_function, &Task3_stack, stackptr_Task3);
constexpr Task t4(4, 4, Task4_function, &Task4_stack, stackptr_Task4);

}; // namespace tasks
}; // namespace os

using namespace os::tasks;

#endif
