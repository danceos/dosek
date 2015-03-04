#ifndef __keso_printf_h__
#define __keso_printf_h__ 1

/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/********************************************************
 * Generated from c-templates/CodeTemplate/kesoPrintf.c *
 ********************************************************/
#include "keso_config_flags.h"

#ifndef KESO_NO_WRITE
#include "keso_types.h"

#define KESO_WRITE(msg, len) keso_write(msg, len)
#define KESO_PRINTF(...) keso_printf(__VA_ARGS__)

int keso_printf(const char *fmt, ...);
unsigned int keso_write(const jchar *buf, unsigned int count);
#else  /* defined(KESO_NO_WRITE) */
#define KESO_WRITE(msg, len)
#define KESO_PRINTF(...)
#endif /* defined(KESO_NO_WRITE) */
#endif
