/* This is a fixup for the following problem:

   - gcc always defines the __UINT* types when it generates defines
     for the __INT* types
   - clang does this not, just because trollin
   - therefore we define the same types, just as unsigned, if they do not exist and do a force
     include for this file.
*/

#ifdef __INT8_TYPE__
#ifndef __UINT8_TYPE__
#define __UINT8_TYPE__ unsigned __INT8_TYPE__
#endif
#endif

#ifdef __INT16_TYPE__
#ifndef __UINT16_TYPE__
#define __UINT16_TYPE__ unsigned __INT16_TYPE__
#endif
#endif

#ifdef __INT32_TYPE__
#ifndef __UINT32_TYPE__
#define __UINT32_TYPE__ unsigned __INT32_TYPE__
#endif
#endif

#ifdef __INT64_TYPE__
#ifndef __UINT64_TYPE__
#define __UINT64_TYPE__ unsigned __INT64_TYPE__
#endif
#endif

#ifdef __INTPTR_TYPE__
#ifndef __UINTPTR_TYPE__
#define __UINTPTR_TYPE__ unsigned __INTPTR_TYPE__
#endif
#endif

