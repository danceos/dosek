/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#include "c15_StringBuilder.h"
#include "c23_String.h"
#include "keso_types.h"
#include "global.h"
#include "domains.h"


/*
 * call analysis 5 c15_StringBuilder_m9_toString
 *
 * c7_HelloWorld_m2_run
 * (valid java/lang/StringBuilder)
 *
 * c7_HelloWorld_m2_run
 * (valid java/lang/StringBuilder)
 *
 * c7_HelloWorld_m2_run
 * (valid java/lang/StringBuilder)
 *
 * c20_Integer_m1_toString
 * (valid java/lang/StringBuilder)
 *
 * c20_Integer_m1_toString
 * (valid java/lang/StringBuilder)
 *
 * total (valid java/lang/StringBuilder)
 */

/* c15_StringBuilder_m9_toString #non_blocking */
/* java/lang/StringBuilder.toString()Ljava/lang/String; */

object_pointer c15_StringBuilder_m9_toString(object_pointer obj0)
{
	object_pointer obj2_0;
	object_pointer obj3_0;
	jint i4_0;
	
/* c15_StringBuilder_m9_toString_B0:  Pred:  No: 1 done */
	
/*==============================================================/
| 62:   return new String(data, 0, length);
/==============================================================*/

	obj2_0 = KESO_ALLOC_C23_STRING();
	obj3_0 = (ACCFIELD_C15_STRINGBUILDER_C15F1_DATA(obj0));
	i4_0 = (ACCFIELD_C15_STRINGBUILDER_C15F2_LENGTH(obj0));
	c23_String_m1__init_(obj2_0, obj3_0, (0), i4_0);
	/* goto c15_StringBuilder_m9_toString_B18 */

	
/* c15_StringBuilder_m9_toString_B18:  Pred:  0 No: 4 done */

	return (object_pointer)obj2_0;

}
