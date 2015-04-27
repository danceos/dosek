#ifndef __ARCH_POSIX_TCB
#define __ARCH_POSIX_TCB

#include  "machine.h"
#include "os/util/assert.h"
#include <stdio.h>

namespace arch { struct TCB; }

extern "C" void kickoff(arch::TCB *);

namespace arch {

struct TCB {
	typedef void (* const fptr_t)(void);

	bool basic_task;

	// task function
	fptr_t fun;

	// task stack
	void * const stack;

	// reference to saved stack pointer
	void* &sp;

	const int stacksize;

	inline void ** get_tos(void) const {
		void **tos = (void **)(((char *)stack) + stacksize);
		return tos;
	}

	inline void* &running_marker(void) const {
		return *(get_tos() - 1);
	}

	inline void* &basic_task_frame_pointer(void) const {
		return *(get_tos() - 2);
	}

	inline void reset(void) const {
		void **tos = get_tos();
		*(--tos) = (void *) 0xaaaaffff; // is fresh

		if (!basic_task) {
			*(--tos) = (void *) this->fun; // current task
			*(--tos) = 0; // %rbx (%ebx)
			*(--tos) = 0; // %r12 (%esi)
			*(--tos) = 0; // %r13 (%edi)
			*(--tos) = 0; // %r14 (%ebp)
			sp = tos;
		}
		assert (!is_running ());
	}

	void switch_to_basic_task(const TCB *old) const {
		// printf("\nto basic_task %p -> %p\n", old ? &(old->sp) : NULL, &sp);
		// We will be running, so we mark ourself as running
		bool must_start_next = !is_running();
		set_running();

		if (old == 0) { /* No task was ever running before */
			basic_task_frame_pointer() = sp;
			asm volatile ("mov %1, %%esp;" // to shared stack
						  "jmp *%0;"      // into task
						  ::
						   "r" (fun),
						   "r" (basic_task_frame_pointer())
						  );
		} else {
			// Are we already on the correct stack?
			if (old->basic_task) {
				// printf("Already on shared stack\n");
				if (must_start_next) {
					// printf("old->is_running = %d\n", old->is_running());
					if (old->is_running()) {
						// Here, we save a context which can be used
						// by switchTo. If the activated BT chains to
						// an extended task, we have resume here
						asm volatile ("push $1f;"
									  "push %%ebx\n"
									  "push %%esi\n"
									  "push %%edi\n"
									  "push %%ebp\n"
									  "mov %%esp, (%0);"
									  "jmp *%1;"
									  "1:"
									  :: "r" (&basic_task_frame_pointer()),
									   "r" (fun)
									  : "memory");
					} else {
						// printf("Replace on Top 0x%x\n", (int)Machine::get_stackptr());
						basic_task_frame_pointer() = old->basic_task_frame_pointer();
						asm volatile ("mov %0, %%esp;"
									  "jmp *%1;"
									  :: "r" (basic_task_frame_pointer()),
									   "r" (fun)
									  : "memory");

					}
				} else {
					// We want to terminate old. We know that the task we want to switch to
					// lifes directly under old's frame pointer. Therefore we use startTo
					// printf("Terminate old task %p\n", old->basic_task_frame_pointer());
					_startTo(&(old->basic_task_frame_pointer()));
				}
			} else { // !Shared Stack
				// We have to switch to the shared stack
				if (must_start_next) {
					// printf("Activate on Shared Stack\n"); We save
					// out context on the extended stack, move to
					// basic stack and jump into the task.
					void *dummy;
					void **save_sp = old->is_running() ? &(old->sp) : &dummy;
					basic_task_frame_pointer() = sp;
					asm volatile (
								  // Save Context on Extended Stack
								  "push $1f;"
								  "push %%ebx\n"
								  "push %%esi\n"
								  "push %%edi\n"
								  "push %%ebp\n"
								  "mov  %%esp, (%0)\n"

								  // to shared stack
								  "mov %2, %%esp;"
								  "jmp *%1;"      // into task
								  // Return Point for extended task
								  "1:\n"
								  ::
								   "r" (save_sp),
								   "r" (fun),
								   "r" (sp)
								  : "memory");
				} else {
					// The old task is already running on shared
					// stack. Therefore, we can simply switch to the
					// saved context on the other stack
					// printf("Resume to shared stack\n");
					_switchTo(&old->sp, &sp);
				}
			}
		}
	}


	void start(const TCB *old) const {
		if (old && old->basic_task) {
			// We switch away from the basic stack. Therefore we have
			// to reset the shared stack pointer
			old->sp = (void*)((int)old->basic_task_frame_pointer());
			//printf("STA with remove old stack %p\n", old->sp);
		}
		set_running();
		// Lets go to an extended stack
		_startTo(&sp);
	}

    void switchTo(const TCB *other) const {
		other->set_running();
		_switchTo(&sp, &(other->sp));
	}

    static noinline void _switchTo(void **from, void **to) {
        asm __volatile__ ("push %%ebx\n"
                          "push %%esi\n"
                          "push %%edi\n"
                          "push %%ebp\n"
                          "mov  %%esp, %0\n"
                          "mov  %1, %%esp\n"
                          "pop  %%ebp\n"
                          "pop  %%edi\n"
                          "pop  %%esi\n"
                          "pop  %%ebx\n"
                          : "=m" (*from)
                          : "m" (*to)
                          : "memory"
                          );
    }

	static noinline void _startTo(void **to) {
		asm __volatile__ ("mov  %0, %%esp\n"
						  "pop  %%ebp\n"
						  "pop  %%edi\n"
						  "pop  %%esi\n"
						  "pop  %%ebx\n"
						  "ret"
						  : 
						  : "m" (*to)
						  : "memory"
						  );
    }


	inline bool is_running(void) const {
		return running_marker() != (void *) 0xaaaaffff;
	}

	inline void set_running() const {
		running_marker() = (void *) 0xa5a5a5a5;
	}


    constexpr TCB(fptr_t f, void *s, void* &sptr, int stacksize)
		: basic_task(stacksize < 16), fun(f), stack(s), sp(sptr),  stacksize(stacksize) {}

};

};
#endif
