/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#include "c26_StringIndexOutOfBoundsException.h"
#include "c29_String.h"
#include "keso_types.h"
#include "global.h"
#include "domains.h"


/*
 * call analysis 1 c29_String_m6_out_of_bounds
 *
 * c29_String_m3_getChars
 * (valid java/lang/Object)
 *
 * total (valid java/lang/Object)
 */

/* c29_String_m6_out_of_bounds #non_blocking */
/* java/lang/String.out_of_bounds()Ljava/lang/StringIndexOutOfBoundsException; */

object_pointer c29_String_m6_out_of_bounds(object_pointer obj0)
{
	object_pointer obj2_0;
	
/* c29_String_m6_out_of_bounds_B0:  Pred:  No: 1 done */
	
/*==============================================================/
| 506:   return new StringIndexOutOfBoundsException();
/==============================================================*/

	obj2_0 = KESO_ALLOC_C26_STRINGINDEXOUTOFBOUNDSEXCEPTION();
	/* goto c29_String_m6_out_of_bounds_B9 */

	
/* c29_String_m6_out_of_bounds_B9:  Pred:  0 No: 3 done */

	return (object_pointer)obj2_0;

}

