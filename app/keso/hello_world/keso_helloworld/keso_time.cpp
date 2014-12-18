/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/********************************************************
 * Generated from c-templates/CodeTemplate/dosek/nano.c *
 ********************************************************/
#include "keso_time.h"

/*
	CoderDOSEK
*/

jlong keso_nanotime(void) {
	julong freq = (julong) 12;
	julong ticks = (julong) 23;
	return (jlong) (ticks * 1000ULL / freq);
}

