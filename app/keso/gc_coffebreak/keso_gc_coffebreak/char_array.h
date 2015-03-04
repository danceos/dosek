#ifndef __char_array_h__
#define __char_array_h__ 1

/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/************************************************************
 * Generated from c-templates/CodeTemplate/primitiveArray.c *
 ************************************************************/
#include "keso_types.h"
#include "global.h"

#define CHAR_ARRAY_ID ((class_id_t) 2)

/* element access macros */
#define CHAR_ARRAY_LEA(array,index) (((char_array_t*)NATIVE_ADDR(array))->data[(index)])
#define CHAR_ARRAY_ALOAD(array,index) CHAR_ARRAY_LEA(array,index)

#ifndef KESO_GET_ARRAY_LENGTH
#define KESO_GET_ARRAY_LENGTH(array) ((jint)(((array_t*)NATIVE_ADDR(array))->size))
#endif

#ifdef PROGMEM
#define CHAR_ARRAY_ALOAD_PGM(array, index) pgm_read_byte(&CHAR_ARRAY_LEA(array, index))
#endif

typedef struct {
	ARRAY_HEADER
	jchar data[1];
} char_array_t;
/*********************************************************************
 * Generated from c-templates/CodeTemplate/primitiveArrayHeapAlloc.c *
 *********************************************************************/
object_t *keso_alloc_char_array(array_size_t);
#endif
