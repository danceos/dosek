/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#ifndef __C10_THROWABLE_H__
#define __C10_THROWABLE_H__
#include "keso_object_pointer.h"
#include "keso_types.h"

#define C10_THROWABLE_ID ((class_id_t)10)

/* object data */
typedef struct {
/* c10_Throwable */
	object_pointer c10f1_message;
/* c1_Object */
OBJECT_HEADER
/* c1_Object */
/* c10_Throwable */
} c10_Throwable_t;
#define C10_THROWABLE_OBJ(_obj_) ((c10_Throwable_t*)((object_pointer*)(_obj_)-1))
#define ACCFIELD_C10_THROWABLE_C10F1_MESSAGE(_obj_) (C10_THROWABLE_OBJ(_obj_)->c10f1_message)
#define KESO_ALLOC_C10_THROWABLE() KESO_ALLOC(C10_THROWABLE_ID,sizeof(c10_Throwable_t),1)
#define KESO_ALLOC_STACK_C10_THROWABLE(_mem_) keso_alloc_stack((object_pointer)&(_mem_), C10_THROWABLE_ID,sizeof(c10_Throwable_t),1)
#define KESO_ALLOC_INLINE_C10_THROWABLE() KESO_ALLOC(C10_THROWABLE_ID,sizeof(c10_Throwable_t),1)

/* class methods prototypes */



#endif /* !defined(__C10_THROWABLE_H__) */