#include "thetasks.h"

/**
 * @file
 * @ingroup scheduler
 * @brief Object instantiation
 */

// task stacks
uint8_t Task1_stack[STACKSIZE];
uint8_t Task2_stack[STACKSIZE];
uint8_t Task3_stack[STACKSIZE];
uint8_t Task4_stack[STACKSIZE];

void* stackptr_Task1 = 0;
void* stackptr_Task2 = 0;
void* stackptr_Task3 = 0;
void* stackptr_Task4 = 0;
