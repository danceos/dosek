/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#ifndef __C9_TASKSERVICE_H__
#define __C9_TASKSERVICE_H__
#include "keso_object_pointer.h"
#include "keso_types.h"

#define C9_TASKSERVICE_ID ((class_id_t)9)

/* object data */
typedef struct {
/* c9_TaskService */
/* c1_Object */
OBJECT_HEADER
/* c1_Object */
/* c9_TaskService */
} c9_TaskService_t;
#define C9_TASKSERVICE_OBJ(_obj_) ((c9_TaskService_t*)(_obj_))

/* class methods prototypes */
/* c9_TaskService_m2_terminate #non_blocking */
/* terminate()I */
jint c9_TaskService_m2_terminate(void);



#endif /* !defined(__C9_TASKSERVICE_H__) */
