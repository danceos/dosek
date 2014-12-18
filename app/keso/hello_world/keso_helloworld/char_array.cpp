/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/************************************************************
 * Generated from c-templates/CodeTemplate/primitiveArray.c *
 ************************************************************/
#include "char_array.h"
#include "domains.h"
#include "keso_parity.h"
/*********************************************************************
 * Generated from c-templates/CodeTemplate/primitiveArrayHeapAlloc.c *
 *********************************************************************/
object_t *keso_alloc_char_array(array_size_t size) {
	array_t *array = (array_t *) KESO_ALLOC(CHAR_ARRAY_ID, sizeof(array_t) + (size * sizeof(jchar)), 0);
	array->size = size;
	KESO_SET_PARITY_ARRAYLENGTH(array);
	return (object_t *) array;
}
