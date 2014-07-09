#include "dependability_service.h"
#include "os/util/assert.h"
#include "atomics.h"

Dependability_Scheduler dep_sched;
// From generator:
extern Checked_Object OS_all_CheckedObjects[];
extern unsigned int OS_all_CheckedObjects_size;
extern unsigned int OS_checkfunction_multiplexer(unsigned int id);

unsigned int crc32(char* bytes, unsigned int len)
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
		currently failes with: LLVM ERROR: Cannot select: intrinsic %llvm.x86.sse42.crc32.32.32
		*/
	}
	return crc32;
}

/* Implementation remark:
 * If more than one thread/core/process checks common checked objects, a
 * checker id can be used that allows to synchronize them in a nonblocking
 * way. Note that the queue needs synchronization, too.
 */
enum {
	checksum_valid = 1,
	checksum_invalid = 0,
	checksum_checked = 4,
};

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

bool check_CheckedObject(unsigned int obj)
{
	unsigned int oldvalid = OS_all_CheckedObjects[obj].valid;
	OS_all_CheckedObjects[obj].valid = checksum_checked;
	arch::atomic_memory_barrier();
	if (OS_all_CheckedObjects[obj].counter) {
		return false;
	}

	unsigned int newchecksum = OS_checkfunction_multiplexer(obj);
	if (oldvalid == checksum_valid &&
		OS_all_CheckedObjects[obj].valid == checksum_checked &&
		newchecksum != OS_all_CheckedObjects[obj].checksum) {
			assert(false);
	}
	OS_all_CheckedObjects[obj].checksum = newchecksum;
	return arch::compare_and_swap(&OS_all_CheckedObjects[obj].valid, checksum_checked, checksum_valid);
}

void dependability_service()
{
	for (;;) {
		// Dequeue next element
		unsigned int element = dep_sched.get_next();
		if (!element)
			continue;

		Dependability_Scheduler::Object_State state =
			(check_CheckedObject(element))
				? Dependability_Scheduler::SUCCESS
				: Dependability_Scheduler::FAILURE
		;

		// Enqueue with new priority
		dep_sched.update(element, state);
	}
}

