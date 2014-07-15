#ifndef _COREDOS_OS_DEPSVC_H_
#define _COREDOS_OS_DEPSVC_H_

struct CHECKEDOBJECTStruct {
};

typedef CHECKEDOBJECTStruct* CheckedObjectType;

extern "C" void OSEKOS_AcquireCheckedObject(struct CHECKEDOBJECTStruct *);
extern "C" void OSEKOS_ReleaseCheckedObject(struct CHECKEDOBJECTStruct *);

#define DeclareCheckedObject(c_type, name)                       \
  c_type name;                                                   \
  struct CHECKEDOBJECTStruct OSEKOS_CHECKEDOBJECT_Struct_##name;

#define AcquireCheckedObject(name)                                  \
  OSEKOS_AcquireCheckedObject(&OSEKOS_CHECKEDOBJECT_Struct_##name); \

#define ReleaseCheckedObject(name)                                  \
  OSEKOS_ReleaseCheckedObject(&OSEKOS_CHECKEDOBJECT_Struct_##name); \

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
	unsigned int crc32(char *bytes, unsigned int length);

	#ifdef DEPENDABILITY_FAILURE_LOGGING
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
