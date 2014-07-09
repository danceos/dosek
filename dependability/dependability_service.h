#ifndef _COREDOS_OS_DEPENDABILITY_SERVICE_H_
#define _COREDOS_OS_DEPENDABILITY_SERVICE_H_

#include "dependability_scheduler.h"

namespace dep {
	/**
	 * \brief Metadata for each checked object
	**/
	struct Checked_Object
	{
		Checked_Object(void *pos, unsigned int length)
				: location(reinterpret_cast<char*>(pos)), size(length) {}
		char *location;
		unsigned int size;
		volatile unsigned int checksum;
		/* For synchronisation */
		volatile unsigned int counter;
		/* Special case */
		volatile unsigned int valid;
	};

	extern Dependability_Scheduler dep_sched;

	/**
	 * \brief Runs the dependability service and does not return.
	**/
	void dependability_service();

	/**
	 * \brief Acquires the checked object and marks any available checksums as
	 *        invalid
	**/
	void acquire_CheckedObject(unsigned int obj_index);

	/**
	 * \brief Releases the checked object and marks any available checksums as
	 *        invalid
	**/
	void release_CheckedObject(unsigned int obj_index);

	/**
	 * \brief Compares the old checksum (if available) against the new one and
	 *        calculates a new one. Fails if a task accessed the checked object.
	**/
	bool check_CheckedObject(Checked_Object *obj);

	/**
	 * \brief Calculates the crc32 checksum of given byte array with given length.
	**/
	unsigned int crc32(char *bytes, unsigned int length);

	/* From generator */
	extern Checked_Object OS_all_CheckedObjects[];
	extern const unsigned int OS_all_CheckedObjects_size;
	extern unsigned int OS_checkfunction_multiplexer(unsigned int id);
}

#endif
