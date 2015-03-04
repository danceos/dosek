/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#include "c23_String.h"
#include "char_array.h"
#include "keso_exceptions.h"
#include "keso_types.h"
#include "global.h"
#include "domains.h"


/*
 * call analysis 3 c23_String_m1__init_
 *
 * c15_StringBuilder_m9_toString
 * (valid java/lang/String, ?null [C, 0, int)
 *
 * c19_Long_m2_toString
 * (valid java/lang/String, valid [C, 19, 1)
 *
 * c19_Long_m2_toString
 * (valid java/lang/String, valid [C, int, int)
 *
 * total (valid java/lang/String, ?null [C, int, int)
 */

/* c23_String_m1__init_ #non_blocking */
/* java/lang/String.<init>([CII)V */

void c23_String_m1__init_(object_pointer obj0, object_pointer obj1, jint i2, jint i3)
{
	object_pointer obj5_0;
	jint i4_1;
	jint i7_0;
	jint i8_0;
	
/* c23_String_m1__init__B0:  Pred:  No: 1 done */
	
/*==============================================================/
| 40:   value = new char[count];
/==============================================================*/


	
/* z33_c23_String_m1__init__B8:  Pred:  0 No: 2 done */

	obj5_0 = keso_alloc_char_array(i3);
	(ACCFIELD_C23_STRING_C23F1_VALUE(obj0)) = (object_pointer)obj5_0;
	i4_1 = (0);

	
c23_String_m1__init__B14: /* Pred:  0 20 No: 4 done */
	
/*==============================================================/
| 41:   for(int i=0; i<count; i++) value[i] = newValue[offset+i];
/==============================================================*/

	if (i4_1>=i3) goto c23_String_m1__init__B41;

	
/* c23_String_m1__init__B20:  Pred:  14 No: 5 done */

	i7_0 = (i2+i4_1);
				KESO_CHECK_CALOAD_NULLPOINTER(obj1,"c23_String_m1__init_",31, 24);

	
/* z35_c23_String_m1__init__B32:  Pred:  20 No: 6 done */

				KESO_CHECK_CALOAD_ARRAY_NOTNULL(obj1,i7_0,"c23_String_m1__init_",31, 25);
	i8_0 = CHAR_ARRAY_ALOAD(obj1, i7_0);
				KESO_CHECK_CASTORE_ARRAY_NOTNULL(obj5_0,i4_1,"c23_String_m1__init_",32, 26);
	CHAR_ARRAY_LEA(obj5_0, i4_1) = i8_0;
	i4_1 = (i4_1+0x1);
	goto c23_String_m1__init__B14;

	
c23_String_m1__init__B41: /* Pred:  14 No: 9 done */
	
/*==============================================================/
| 42:  }
/==============================================================*/

	return;

}
