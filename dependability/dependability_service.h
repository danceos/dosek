#ifndef _COREDOS_OS_DEPENDABILITY_SERVICE_H_
#define _COREDOS_OS_DEPENDABILITY_SERVICE_H_

#include "dependability_scheduler.h"

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
	volatile unsigned int dirty; /* XXX: Replaced by valid */
	volatile unsigned int counter;
	volatile unsigned int version; /* XXX: Probably not required */
	/* Special case */
	volatile unsigned int valid;
};

extern Dependability_Scheduler dep_sched;

/**
 * \brief Runs the dependability service and does not return.
**/
extern "C" void dependability_service();

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

#endif
