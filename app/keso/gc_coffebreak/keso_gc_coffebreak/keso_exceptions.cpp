/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/******************************************************************
 * Generated from c-templates/CodeTemplate/exceptions/array_chk.c *
 ******************************************************************/
#include "keso_exceptions.h"
#include "global.h"

#ifndef KESO_OMIT_SAFECHECKS
#ifndef KESO_PRODUCTION

#include "keso_types.h"
#include "keso_printf.h"
#include "keso_os.h" // for E_NOT_OK

void keso_throw_index_out_of_bounds(const char* method, int bcpos) {
	KESO_PRINTF("index out of bounds exception (%s, BCP %d)\n", method, bcpos);
	ShutdownOS(E_NOT_OK);
}
#endif
#endif
/**********************************************************************
 * Generated from c-templates/CodeTemplate/exceptions/arraysize_chk.c *
 **********************************************************************/
#include "keso_exceptions.h"

#ifndef KESO_OMIT_SAFECHECKS
#ifndef KESO_PRODUCTION

#include "keso_printf.h"
#include "keso_types.h"
#include "keso_os.h" // for E_NOT_OK

void keso_throw_negative_array_size(const char* method, int bcpos) {
	KESO_PRINTF("negative array size exception (%s, BCP %d)\n", method, bcpos);
	ShutdownOS(E_NOT_OK);
}
#endif
#endif
/******************************************************************
 * Generated from c-templates/CodeTemplate/exceptions/error_chk.c *
 ******************************************************************/
#include "keso_exceptions.h"
#include "global.h"
#include "keso_os.h" // for E_NOT_OK

#ifdef KESO_PRODUCTION
	void keso_throw_error(void) {
		ShutdownOS(E_NOT_OK);
	}
#else /* defined(KESO_PRODUCTION) */
	#include "keso_printf.h"

	void keso_throw_error(const char *msg) {
		KESO_PRINTF("%s\n", msg);
		KESO_PRINT_STACKTRACE();
		ShutdownOS(E_NOT_OK);
	}
#endif /* defined(KESO_PRODUCTION) */
/*****************************************************************
 * Generated from c-templates/CodeTemplate/exceptions/null_chk.c *
 *****************************************************************/
#include "keso_exceptions.h"

#ifndef KESO_OMIT_SAFECHECKS
#ifndef KESO_PRODUCTION

#include "keso_printf.h"
#include "keso_types.h"
#include "keso_os.h" // for E_NOT_OK

void keso_throw_nullpointer(const char* method, int bcpos) {
	KESO_PRINTF("null pointer exception (%s, BCP %d)\n", method, bcpos);
	ShutdownOS(E_NOT_OK);
}

void keso_check_obj(object_pointer obj) {
	if (obj == (void *) 0) {
		KESO_PRINTF("null pointer exception\n");
		while (1) {};
	}
	if (!(0 < (obj->class_id) && (obj->class_id) < MAXCLASSID)) {
		KESO_PRINTF("Pointer is not an valid object reference!\n");
		while (1) {};
	}
}

#endif
#endif
