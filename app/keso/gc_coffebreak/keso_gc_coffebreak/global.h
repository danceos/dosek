/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#ifndef _GLOBAL_H_
#define _GLOBAL_H_ 1

#include "keso_types.h"
#define keso_throw_method_not_implemented(method, bcpos) (keso_throw_error("method " method " not implemented"), NULL)
#include "keso_os.h"
#include "keso_config_flags.h"
/* adjust this value to your needs! */
#define KESO_TICKS_MICRO 1995
#include "keso_compiler_extensions.h"
#include "keso_compiler_extensions.h"
#include <stddef.h>
#define KESO_OFFSETOF_ASSERT( S, M, O ) KESO_STATIC_ASSERT( offsetof( S, M ) == (O), wrong_offset_for_##S##_##M )
#include "keso_object.h"
#include "keso_object_pointer.h"
#include "keso_llref_stack.h"
typedef array_t *array_pointer;
typedef const array_t *const_array_pointer;
/* KESO_DUP_OBJ_MAX is the maximum of recursion depth
 * for object copy in portal calls */
#ifndef KESO_DUP_OBJ_MAX
#define KESO_DUP_OBJ_MAX 10
#endif
/* KESO_COMP_OBJ_MAX is the maximum of recursion depth
 * for object comparison in portal calls */
#ifndef KESO_COMP_OBJ_MAX
#define KESO_COMP_OBJ_MAX 15
#endif
#define KESO_OBJ_PTR(_roff_, _mem_) (object_pointer)((object_pointer*)(_mem_)+(_roff_))
#define KESO_TOP_PTR(_roff_, _obj_) (jbyte*)((object_pointer*)(_obj_)-(_roff_))
#define KESO_REF_PTR(_roff_, _obj_) (object_pointer*)((object_pointer*)(_obj_)-(_roff_))

/* static accesses */
/* keso/io/DebugOut c7f1_buf rw obj0_0 */

/* field accesses */
/* java/lang/String c29f1_value rw  */
/* test/HelloWorld c5f1_runs rw  */
/* test/QueueElement c9f1_next rw  */
/* test/QueueElement c9f2_value rw  */
/* java/lang/StringBuilder c8f2_length rw  */
/* java/lang/StringBuilder c8f1_data rw  */
#include "keso_printf.h"
#include "keso_parity.h"
#define KESO_NUMBER_OF_TASKS 2
#define KESO_LOCK(_obj_) (void)_obj_
#define KESO_UNLOCK(_obj_) (void)_obj_

#define keso_isObjectArrayClass(_class_id_) (0)
#define keso_isArrayClass(_class_id_) (1<(_class_id_)&&(_class_id_)<3)
#define KESO_HAS_ARRAYS 1

/* not available #define KESO_MEMORYOBJECT_AVAILABLE */
#define keso_isMemoryClass(_class_id_) (0)
#define KESO_MEMORY_ADDR(_obj_) (0)
#define KESO_MEMORY_SIZE(_obj_) (0)
extern  KESO_CONST code_t dispatch_table[];
#ifndef KESO_NEED_FINALIZE
#define KESO_INVOKE_FINALIZE(_self_)(_self_)
#endif
#define CLS_ROFF(_cls_) CLASS(_cls_).roff
#define CLS_SIZE(_cls_) CLASS(_cls_).size
#define CLS_IFACES(_cls_) CLASS(_cls_).ifaces
typedef struct {
	obj_size_t     size;
/* class info for bidirectional object layout */
	unsigned char roff;
} class_t;

#define CLASS(_id_) class_store[((_id_)-1)]
extern KESO_CONST class_t class_store[];
#define C1_OBJECT_RANGE 37
#define CHAR_ARRAY_RANGE 2
#define C3_INPUTSTREAM_RANGE 3
#define C4_ALARM_RANGE 4
#define C5_HELLOWORLD_RANGE 5
#define C6_THREAD_RANGE 6
#define C7_DEBUGOUT_RANGE 7
#define C8_STRINGBUILDER_RANGE 8
#define C9_QUEUEELEMENT_RANGE 9
#define C10_NUMBER_RANGE 11
#define C11_INTEGER_RANGE 11
#define C12_OSSERVICE_RANGE 12
#define C13_CHARACTER_RANGE 13
#define C14_EVENTS_RANGE 14
#define C15_MATH_RANGE 15
#define C16_PORTALSERVICE_RANGE 16
#define C17_OUTPUTSTREAM_RANGE 22
#define C18_FILTEROUTPUTSTREAM_RANGE 21
#define C19_PRINTSTREAM_RANGE 21
#define C20_DEBUGOUTPRINTSTREAM_RANGE 20
#define C21_NULLPRINTSTREAM_RANGE 21
#define C22_DEBUGOUTOUTPUTSTREAM_RANGE 22
#define C23_THROWABLE_RANGE 26
#define C24_EXCEPTION_RANGE 26
#define C25_RUNTIMEEXCEPTION_RANGE 26
#define C26_STRINGINDEXOUTOFBOUNDSEXCEPTION_RANGE 26
#define C27_GC_RANGE 27
#define C28_EVENTSERVICE_RANGE 28
#define C29_STRING_RANGE 29
#define C30_CLASS_RANGE 30
#define C31_CONFIG_RANGE 31
#define C32_SYSTEM_RANGE 32
#define KESO_CLASSSTORE_SIZE 31
#define MAXCLASSID (32)
#define ASSERTCLASSID(_id_) KESO_ASSERT(0<(_id_) && (_id_)<32)
#define ASSERTOBJ(_obj_)
#include "c29_String.h"
#include "char_array.h"
extern c29_String_t str1;
extern c29_String_t str0;
extern c29_String_t str2;
extern c29_String_t str3;

/* translation callbacks */
#define KESO_GCMODE_LAZY 1
#define KESO_HEAP_HAS_TINY_SLOTS 1
#define keso_isStackRef(_ref_) ((unsigned int)(_ref_)&0x1)
#define keso_unpackStackRef(_ref_) (object_pointer*)((unsigned int)(_ref_)-1)
#include "domains.h"
#include "keso_time_stats.h"


/* Task management */

#include "c6_Thread.h"
extern c6_Thread_t ALIGN4 __DOSEK_APPDATA_dom1__task1_obj;


/* Alarm management */

#include "c4_Alarm.h"
extern c4_Alarm_t ALIGN4 __DOSEK_APPDATA_dom1__alarm1_obj;
#define KESO_TASKCLASSTYPE c6_Thread_t
#define KESO_TASKCLASSID C6_THREAD_ID


/* usercode task objects */

#include "c5_HelloWorld.h"
extern c5_HelloWorld_t ALIGN4 __DOSEK_APPDATA_dom1__task1_user_obj;
#define KESO_CURRENT_TASK keso_curr_task
#define KESO_INVALID_TASK ((KESO_TASKCLASSTYPE*) ((object_pointer*)NULL - 0))
#define KESO_SET_CURRENT_TASK(_x_) keso_curr_task= (KESO_TASKCLASSTYPE*) ((object_pointer*)(_x_) - 0)
#define KESO_GET_CURRENT_TASK() (object_pointer) ((object_pointer*) keso_curr_task + 0)
extern KESO_TASKCLASSTYPE *keso_curr_task;
KESO_TASKCLASSTYPE *keso_curr_task_fkt(void);

#define KESO_MAX_TASK 3
extern c6_Thread_t* keso_task_index[KESO_MAX_TASK];
#include "keso_os.h"

#define KESO_NUM_CHECKS 23

#endif
