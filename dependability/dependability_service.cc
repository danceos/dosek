#include "dependability_service.h"
#include "os/util/assert.h"
#include "atomics.h"

Dependability_Queue<Checked_Object> dep_queue;

static inline unsigned int crc32(char* bytes, unsigned int len)
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

void acquire_CheckedObject(Checked_Object *obj)
{
	arch::atomic_fetch_and_add(&obj->counter, 1);
	obj->valid = checksum_invalid;
}

void release_CheckedObject(Checked_Object *obj)
{
	arch::atomic_fetch_and_sub(&obj->counter, 1);
	obj->valid = checksum_invalid;
}

bool check_CheckedObject(Checked_Object *obj)
{
	unsigned int oldvalid = obj->valid;
	obj->valid = checksum_checked;
	arch::atomic_memory_barrier();
	if (obj->counter) {
		return false;
	}

	unsigned int newchecksum = crc32(obj->location, obj->size);
	if (oldvalid == checksum_valid &&
		obj->valid == checksum_checked &&
		newchecksum != obj->checksum) {
			assert(false);
	}
	obj->checksum = newchecksum;
	return arch::compare_and_swap(&obj->valid, checksum_checked, checksum_valid);
}

void dependability_service()
{
	for (;;) {
		// Dequeue next element
		Checked_Object *element = dep_queue.get_next();
		if (!element)
			continue;

		Dependability_Queue<Checked_Object>::Object_State state =
			(check_CheckedObject(element))
				? Dependability_Queue<Checked_Object>::SUCCESS
				: Dependability_Queue<Checked_Object>::FAILED
		;

		// Enqueue with new priority
		dep_queue.insert(element, state);
	}
}

