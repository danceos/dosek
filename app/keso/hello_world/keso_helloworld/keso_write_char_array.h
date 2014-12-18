#ifndef __keso_write_char_array_h__
#define __keso_write_char_array_h__ 1

/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/****************************************************************
 * Generated from c-templates/CodeTemplate/kesoWriteCharArray.c *
 ****************************************************************/
#include "keso_config_flags.h"

#ifndef KESO_NO_WRITE
#include "keso_object.h"
#include "keso_printf.h"
/*void keso_write_char_array(char_array_t *array);*/
#define KESO_WRITE_CHAR_ARRAY(array,length) KESO_WRITE((jchar*)((array)->data),length)
#else
#define keso_write_char_array(array,length) ((void)array)
#endif
#endif
