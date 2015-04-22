#include "dependability_service.h"
#include "os/util/assert.h"
#include "atomics.h"

namespace dep {

#ifdef CONFIG_DEPENDABILITY_FAILURE_LOGGING
			volatile unsigned int failure_counter = 0;
			volatile unsigned int check_counter   = 0;
			#define DEPLOG(state)                              \
				++check_counter;                               \
				if (state == Dependability_Scheduler::FAILURE) \
						++failure_counter;                     \
				(void) check_counter;                          \
				(void) failure_counter;
				/* The two lines above somehow force the change of
				 * check_counter and failure_counter!?
				 */
#else
			#define DEPLOG(state)
#endif

	Dependability_Scheduler dep_sched;
	// From generator:
	unsigned int crc32(const char* bytes, unsigned int len)
	{
		unsigned int crc32 = 0;
		for (unsigned int i = 0; i < len * 8; ++i) {
			if (((crc32 & (1 << (sizeof(crc32) * 8 - 1))) >> (sizeof(crc32) * 8 - 1))
					== ((bytes[i / 8] >> (i % 8)) & 1)) {
				crc32 = (crc32 << 1) ^ 0x04C11DB7;
			} else {
				crc32 <<= 1;
			}
			/*
			crc32 = __builtin_ia32_crc32si(crc32, bytes[i]);
			currently fails with: LLVM ERROR: Cannot select: intrinsic %llvm.x86.sse42.crc32.32.32
			*/
		}
		return crc32;
	}

	void acquire_CheckedObject(unsigned int obj_index)
	{
		arch::atomic_fetch_and_add(&OS_all_CheckedObjects[obj_index].counter, 1);
		OS_all_CheckedObjects[obj_index].valid = checksum_invalid;
	}

	void release_CheckedObject(unsigned int obj_index)
	{
		arch::atomic_fetch_and_sub(&OS_all_CheckedObjects[obj_index].counter, 1);
		OS_all_CheckedObjects[obj_index].valid = checksum_invalid;
	}

	void release_all_CheckedObjects()
	{
		for (unsigned int i = 0; i < OS_all_CheckedObjects_size; ++i) {
			OS_all_CheckedObjects[i].counter = 0;
		}
	}

	bool check_CheckedObject(unsigned int obj)
	{
		unsigned int oldvalid = OS_all_CheckedObjects[obj].valid;
		OS_all_CheckedObjects[obj].valid = checksum_checked;
		arch::atomic_memory_barrier();
		if (OS_all_CheckedObjects[obj].counter) {
			return false;
		}

		unsigned int newchecksum = OS_checkfunction_multiplexer(obj);
		if ((oldvalid == checksum_valid &&
			OS_all_CheckedObjects[obj].valid == checksum_checked &&
			newchecksum != OS_all_CheckedObjects[obj].checksum) ||
			((OS_all_CheckedObjects[obj].valid != checksum_invalid) &&
			(OS_all_CheckedObjects[obj].valid != checksum_valid) &&
			(OS_all_CheckedObjects[obj].valid != checksum_checked))) {
				assert(false);
		}
		OS_all_CheckedObjects[obj].checksum = newchecksum;
		return arch::compare_and_swap(&OS_all_CheckedObjects[obj].valid, checksum_checked, checksum_valid);
	}

	void dependability_service() {
		for (;;) {
			// Dequeue next element
		unsigned int element = dep_sched.get_next();
			Dependability_Scheduler::Object_State state =
				(check_CheckedObject(element))
					? Dependability_Scheduler::SUCCESS
					: Dependability_Scheduler::FAILURE
			;

			DEPLOG(state);

			// Enqueue with new priority
			dep_sched.update(element, state);
		}
	}
}
