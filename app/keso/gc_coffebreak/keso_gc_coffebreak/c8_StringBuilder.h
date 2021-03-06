/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#ifndef __C8_STRINGBUILDER_H__
#define __C8_STRINGBUILDER_H__
#include "keso_object_pointer.h"
#include "keso_types.h"

#define C8_STRINGBUILDER_ID ((class_id_t)8)

/* object data */
typedef struct {
/* c8_StringBuilder */
	object_pointer c8f1_data;
/* c1_Object */
OBJECT_HEADER
/* c1_Object */
	jint c8f2_length;
/* c8_StringBuilder */
} c8_StringBuilder_t;
#define C8_STRINGBUILDER_OBJ(_obj_) ((c8_StringBuilder_t*)((object_pointer*)(_obj_)-1))
#define ACCFIELD_C8_STRINGBUILDER_C8F1_DATA(_obj_) (C8_STRINGBUILDER_OBJ(_obj_)->c8f1_data)
#define ACCFIELD_C8_STRINGBUILDER_C8F2_LENGTH(_obj_) (C8_STRINGBUILDER_OBJ(_obj_)->c8f2_length)
#define KESO_ALLOC_C8_STRINGBUILDER() KESO_ALLOC(C8_STRINGBUILDER_ID,sizeof(c8_StringBuilder_t),1)
#define KESO_ALLOC_STACK_C8_STRINGBUILDER(_mem_) keso_alloc_stack((object_pointer)&(_mem_), C8_STRINGBUILDER_ID,sizeof(c8_StringBuilder_t),1)
#define KESO_ALLOC_INLINE_C8_STRINGBUILDER() KESO_ALLOC(C8_STRINGBUILDER_ID,sizeof(c8_StringBuilder_t),1)

/* class methods prototypes */
/* c8_StringBuilder_m6_ensureCapacity #non_blocking */
/* ensureCapacity(I)V */
void c8_StringBuilder_m6_ensureCapacity(object_pointer obj0, jint i1);
/* c8_StringBuilder_m3__init_ #non_blocking */
/* <init>()V */
void c8_StringBuilder_m3__init_(object_pointer obj0);
/* c8_StringBuilder_m8_append #non_blocking */
/* append(I)Ljava/lang/StringBuilder; */
object_pointer c8_StringBuilder_m8_append(object_pointer obj0, jint i1);
/* c8_StringBuilder_m9_toString #non_blocking */
/* toString()Ljava/lang/String; */
object_pointer c8_StringBuilder_m9_toString(object_pointer obj0);
/* c8_StringBuilder_m1_append #non_blocking */
/* append(Ljava/lang/String;)Ljava/lang/StringBuilder; */
object_pointer c8_StringBuilder_m1_append(object_pointer obj0, object_pointer obj1);
/* c8_StringBuilder_m10_append #non_blocking */
/* append(C)Ljava/lang/StringBuilder; */
object_pointer c8_StringBuilder_m10_append(object_pointer obj0, jint i1);



#endif /* !defined(__C8_STRINGBUILDER_H__) */
