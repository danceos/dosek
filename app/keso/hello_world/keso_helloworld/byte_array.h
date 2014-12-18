#ifndef __byte_array_h__
#define __byte_array_h__ 1

/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/************************************************************
 * Generated from c-templates/CodeTemplate/primitiveArray.c *
 ************************************************************/
#include "keso_types.h"
#include "global.h"

#define BYTE_ARRAY_ID ((class_id_t) 2)

/* element access macros */
#define BYTE_ARRAY_LEA(array,index) (((byte_array_t*)NATIVE_ADDR(array))->data[(index)])
#define BYTE_ARRAY_ALOAD(array,index) BYTE_ARRAY_LEA(array,index)

#ifndef KESO_GET_ARRAY_LENGTH
#define KESO_GET_ARRAY_LENGTH(array) ((jint)(((array_t*)NATIVE_ADDR(array))->size))
#endif

#ifdef PROGMEM
#define BYTE_ARRAY_ALOAD_PGM(array, index) pgm_read_byte(&BYTE_ARRAY_LEA(array, index))
#endif

typedef struct {
	ARRAY_HEADER
	jbyte data[1];
} byte_array_t;
#endif
