/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#ifndef __C24_CONFIG_H__
#define __C24_CONFIG_H__
#include "keso_object_pointer.h"
#include "keso_types.h"

#define C24_CONFIG_ID ((class_id_t)24)

/* object data */
typedef struct {
/* c24_Config */
/* c1_Object */
OBJECT_HEADER
/* c1_Object */
/* c24_Config */
} c24_Config_t;
#define C24_CONFIG_OBJ(_obj_) ((c24_Config_t*)(_obj_))
#define KESO_ALLOC_C24_CONFIG() KESO_ALLOC(C24_CONFIG_ID,sizeof(c24_Config_t),0)
#define KESO_ALLOC_STACK_C24_CONFIG(_mem_) keso_alloc_stack((object_pointer)&(_mem_), C24_CONFIG_ID,sizeof(c24_Config_t),0)
#define KESO_ALLOC_INLINE_C24_CONFIG() KESO_ALLOC(C24_CONFIG_ID,sizeof(c24_Config_t),0)

/* class methods prototypes */



#endif /* !defined(__C24_CONFIG_H__) */
