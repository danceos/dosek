/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#include "c20_Integer.h"
#include "c30_DebugOutPrintStream.h"
#include "c8_DebugOut.h"
#include "keso_types.h"
#include "global.h"
#include "domains.h"


/*
 * call analysis 1 c30_DebugOutPrintStream_m8_println
 *
 * c7_HelloWorld_m2_run
 * (valid java/io/PrintStream, int)
 *
 * total (valid java/io/PrintStream, int)
 */

/* c30_DebugOutPrintStream_m8_println #non_blocking */
/* keso/io/DebugOutPrintStream.println(I)V */

void c30_DebugOutPrintStream_m8_println(object_pointer obj0, jint i1)
{
	object_pointer obj3;
	
/* c30_DebugOutPrintStream_m8_println_B0:  Pred:  No: 1 done */
	
/*==============================================================/
| 93:   DebugOut.println(v);
| 94:  }
/==============================================================*/

	obj3 = c20_Integer_m1_toString(i1);
	c8_DebugOut_m6_println(obj3);
	/* goto c30_DebugOutPrintStream_m8_println_B6 */

	
/* c30_DebugOutPrintStream_m8_println_B6:  Pred:  0 No: 2 done */

	return;

}

