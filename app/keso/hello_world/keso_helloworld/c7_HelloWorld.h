/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#ifndef __C7_HELLOWORLD_H__
#define __C7_HELLOWORLD_H__
#include "keso_object_pointer.h"
#include "keso_types.h"

#define C7_HELLOWORLD_ID ((class_id_t)7)

/* object data */
typedef struct {
/* c7_HelloWorld */
	object_pointer c7f3_aobj;
/* c1_Object */
OBJECT_HEADER
/* c1_Object */
	jlong c7f1_start;
	jlong c7f2_stop;
/* c7_HelloWorld */
} c7_HelloWorld_t;
#define C7_HELLOWORLD_OBJ(_obj_) ((c7_HelloWorld_t*)((object_pointer*)(_obj_)-1))
#define ACCFIELD_C7_HELLOWORLD_C7F3_AOBJ(_obj_) (C7_HELLOWORLD_OBJ(_obj_)->c7f3_aobj)
#define ACCFIELD_C7_HELLOWORLD_C7F1_START(_obj_) (C7_HELLOWORLD_OBJ(_obj_)->c7f1_start)
#define ACCFIELD_C7_HELLOWORLD_C7F2_STOP(_obj_) (C7_HELLOWORLD_OBJ(_obj_)->c7f2_stop)
#define KESO_ALLOC_C7_HELLOWORLD() KESO_ALLOC(C7_HELLOWORLD_ID,sizeof(c7_HelloWorld_t),1)
#define KESO_ALLOC_STACK_C7_HELLOWORLD(_mem_) keso_alloc_stack((object_pointer)&(_mem_), C7_HELLOWORLD_ID,sizeof(c7_HelloWorld_t),1)
#define KESO_ALLOC_INLINE_C7_HELLOWORLD() KESO_ALLOC(C7_HELLOWORLD_ID,sizeof(c7_HelloWorld_t),1)

/* class methods prototypes */
/* c7_HelloWorld_m1__init_ #non_blocking */
/* <init>()V */
void c7_HelloWorld_m1__init_(object_pointer obj0);
/* c7_HelloWorld_m2_run #non_blocking */
/* run()V */
void c7_HelloWorld_m2_run(object_pointer obj0);
#include "c23_String.h"
extern c23_String_t ALIGN4 c7_HelloWorld_m2_run_str7;



#endif /* !defined(__C7_HELLOWORLD_H__) */