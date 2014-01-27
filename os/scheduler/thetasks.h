// TODO: this file will be generated from the application configuration!

#include "task.h"
#ifndef THETASKS
#define THETASKS

using os::scheduler::Task;

// task handlers
extern "C" __attribute__((weak_import)) void OSEKOS_TASK_Task1(void);
extern "C" __attribute__((weak_import)) void OSEKOS_TASK_Task2(void);
extern "C" __attribute__((weak_import)) void OSEKOS_TASK_Task3(void);
extern "C" __attribute__((weak_import)) void OSEKOS_TASK_Task4(void);

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
constexpr Task t1(1, 2, OSEKOS_TASK_Task1, &Task1_stack, stackptr_Task1);
constexpr Task t2(2, 3, OSEKOS_TASK_Task2, &Task2_stack, stackptr_Task2);
constexpr Task t3(3, 1, OSEKOS_TASK_Task3, &Task3_stack, stackptr_Task3);
constexpr Task t4(4, 4, OSEKOS_TASK_Task4, &Task4_stack, stackptr_Task4);

}; // namespace tasks
}; // namespace os

using namespace os::tasks;

#endif
