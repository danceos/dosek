#ifndef _COREDOS_OS_DEPSVC_H_
#define _COREDOS_OS_DEPSVC_H_

typedef uint32_t CheckedObjectType;

extern "C" void OSEKOS_AcquireCheckedObject(CheckedObjectType object);
extern "C" void OSEKOS_ReleaseCheckedObject(CheckedObjectType object);

#define DeclareCheckedObject(c_type, name)                       \
  c_type name;                                                   \
  extern const uint32_t OSEKOS_CHECKEDOBJECT_##name;

#define AcquireCheckedObject(name)                                  \
  OSEKOS_AcquireCheckedObject(OSEKOS_CHECKEDOBJECT_##name); \

#define ReleaseCheckedObject(name)                                  \
  OSEKOS_ReleaseCheckedObject(OSEKOS_CHECKEDOBJECT_##name); \

namespace dep {
	/**
	 * \brief Runs the dependability service and does not return.
	**/
	void dependability_service();

	/**
	 * \brief Releases all previously aquired and not yet released CheckedObjects.
	 *
	 * Should be called in the PreIdleHook to avoid problems with bitrot while
	 * synchrizing with the dependability service.
	**/
	void release_all_CheckedObjects();

	/** \brief Calculates the crc32 checksum of the given data **/
	unsigned int crc32(const char *bytes, unsigned int length);

#ifdef CONFIG_DEPENDABILITY_FAILURE_LOGGING
		extern volatile unsigned int failure_counter;
		extern volatile unsigned int check_counter;
		#define GET_DEPENDABILITY_FAILURE_COUNT() dep::failure_counter
		#define GET_DEPENDABILITY_CHECK_COUNT() dep::check_counter
#else
		#define GET_DEPENDABILITY_FAILURE_COUNT() ~0
		#define GET_DEPENDABILITY_CHECK_COUNT() 0
#endif
}

#endif
