/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#include "c7_DebugOut.h"
#include "c8_StringBuilder.h"
#include "char_array.h"
#include "keso_exceptions.h"
#include "keso_types.h"
#include "global.h"
#include "domains.h"


/*
 * call analysis 2 c7_DebugOut_m5_println
 *
 * c7_DebugOut_m7_println
 * (?null java/lang/String)
 *
 * c5_HelloWorld_m3_run
 * (?null java/lang/String)
 *
 * total (?null java/lang/String)
 */

/* c7_DebugOut_m5_println #non_blocking */
/* keso/io/DebugOut.println(Ljava/lang/String;)V */

void c7_DebugOut_m5_println(object_pointer obj0)
{
	object_pointer obj1_0;
	object_pointer obj4;
	jint i5;
	object_pointer obj7;
	
/* c7_DebugOut_m5_println_B0:  Pred:  No: 1 done */
	
/*==============================================================/
| 91:   buf.append(msg);
| 92:   println();
/==============================================================*/

	obj1_0 = SC7_DEBUGOUT_C7F1_BUF(((domain_t *) &__DOSEK_APPDATA_dom1__DDesc));
	c8_StringBuilder_m1_append(obj1_0, obj0);
	c8_StringBuilder_m1_append(obj1_0, ((object_pointer) ((object_pointer*) &str0+1)));
	c7_DebugOut_m2_raw_print(obj1_0);
	c8_StringBuilder_m6_ensureCapacity(obj1_0, (0));
	if ((0)<=(ACCFIELD_C8_STRINGBUILDER_C8F2_LENGTH(obj1_0))) goto z31_c8_StringBuilder_m2_setLength_B45;

	
/* z28_c8_StringBuilder_m2_setLength_B17:  Pred:  0 No: 4 done */

	i5 = (ACCFIELD_C8_STRINGBUILDER_C8F2_LENGTH(obj1_0));

	
z13_c8_StringBuilder_m2_setLength_B18: /* Pred:  13 29 No: 5 done */

	if (i5>=(0)) goto z33_c8_StringBuilder_m2_setLength_B48;

	
/* z29_c8_StringBuilder_m2_setLength_B29:  Pred:  18 No: 7 done */

	obj4 = (ACCFIELD_C8_STRINGBUILDER_C8F1_DATA(obj1_0));
				KESO_CHECK_CASTORE_NULLPOINTER(obj4,"c7_DebugOut_m5_println",8, 1);

	
/* z30_c8_StringBuilder_m2_setLength_B29:  Pred:  23 No: 8 done */

				KESO_CHECK_CASTORE_ARRAY_NOTNULL(obj4,i5,"c7_DebugOut_m5_println",8, 2);
	CHAR_ARRAY_LEA(obj4, i5) = (0);
	i5 = (i5+0x1);
	goto z13_c8_StringBuilder_m2_setLength_B18;

	
z31_c8_StringBuilder_m2_setLength_B45: /* Pred:  0 No: 14 done */

	obj7 = (ACCFIELD_C8_STRINGBUILDER_C8F1_DATA(obj1_0));
				KESO_CHECK_CASTORE_NULLPOINTER(obj7,"c7_DebugOut_m5_println",8, 3);

	
/* z32_c8_StringBuilder_m2_setLength_B45:  Pred:  39 No: 15 done */

				KESO_CHECK_CASTORE_ARRAY_NOTNULL(obj7,0,"c7_DebugOut_m5_println",8, 4);
	CHAR_ARRAY_LEA(obj7, (0)) = (0);

	
z33_c8_StringBuilder_m2_setLength_B48: /* Pred:  45 18 No: 11 done */
	
/*==============================================================/
| 93:  }
/==============================================================*/

	(ACCFIELD_C8_STRINGBUILDER_C8F2_LENGTH(obj1_0)) = (jint)(0);
	/* goto c7_DebugOut_m5_println_B13 */

	
/* c7_DebugOut_m5_println_B13:  Pred:  46 No: 12 done */

	return;

}
