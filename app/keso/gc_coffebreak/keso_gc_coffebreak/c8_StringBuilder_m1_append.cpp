/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#include "c29_String.h"
#include "c8_StringBuilder.h"
#include "keso_exceptions.h"
#include "keso_types.h"
#include "global.h"
#include "domains.h"


/*
 * call analysis 7 c8_StringBuilder_m1_append
 *
 * c7_DebugOut_m5_println
 * (valid java/lang/StringBuilder, ?null java/lang/Object)
 *
 * c7_DebugOut_m5_println
 * (valid java/lang/StringBuilder, "
" java/lang/String)
 *
 * c8_StringBuilder_m8_append
 * (valid java/lang/Object, ?null java/lang/String)
 *
 * c5_HelloWorld_m2_printList
 * (valid java/lang/StringBuilder, "	" java/lang/String)
 *
 * c5_HelloWorld_m2_printList
 * (valid java/lang/StringBuilder, ", " java/lang/String)
 *
 * c5_HelloWorld_m2_printList
 * (valid java/lang/StringBuilder, ?null java/lang/String)
 *
 * c5_HelloWorld_m3_run
 * (valid java/lang/StringBuilder, "Queue Run " java/lang/String)
 *
 * total (valid java/lang/Object, ?null java/lang/Object)
 */

/* c8_StringBuilder_m1_append #non_blocking */
/* java/lang/StringBuilder.append(Ljava/lang/String;)Ljava/lang/StringBuilder; */

object_pointer c8_StringBuilder_m1_append(object_pointer obj0, object_pointer obj1)
{
	jint i4_0;
	object_pointer obj5_0;
	jint i6_0;
	jint i4_1;
	jint i15;
	object_pointer obj17;
	
/* c8_StringBuilder_m1_append_B0:  Pred:  No: 1 done */
	
/*==============================================================/
| 133:   int n = str.length();
/==============================================================*/

	obj17 = (ACCFIELD_C29_STRING_C29F1_VALUE(obj1));
				KESO_CHECK_ARRAYLENGTH_NULLPOINTER(obj17,"c8_StringBuilder_m1_append",12, 11);

	
/* z57_c8_StringBuilder_m1_append_B5:  Pred:  0 No: 7 done */
	
/*==============================================================/
| 134:   ensureCapacity(length + n);
| 135:   str.getChars(0, n, data, length);
| 136:   length += n;
: 137: 
| 138:   return this;
/==============================================================*/

	i15 = KESO_GET_ARRAY_LENGTH(obj17);
	i4_0 = ((ACCFIELD_C8_STRINGBUILDER_C8F2_LENGTH(obj0))+i15);
	c8_StringBuilder_m6_ensureCapacity(obj0, i4_0);
	obj5_0 = (ACCFIELD_C8_STRINGBUILDER_C8F1_DATA(obj0));
	i6_0 = (ACCFIELD_C8_STRINGBUILDER_C8F2_LENGTH(obj0));
	c29_String_m3_getChars(obj1, i15, obj5_0, i6_0);
	i4_1 = ((ACCFIELD_C8_STRINGBUILDER_C8F2_LENGTH(obj0))+i15);
	(ACCFIELD_C8_STRINGBUILDER_C8F2_LENGTH(obj0)) = (jint)i4_1;
	/* goto c8_StringBuilder_m1_append_B53 */

	
/* c8_StringBuilder_m1_append_B53:  Pred:  4 No: 4 done */

	return (object_pointer)obj0;

}
