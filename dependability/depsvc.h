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

unsigned int crc32(char *bytes, unsigned int length);

#endif
