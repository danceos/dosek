/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#include "c30_DebugOutPrintStream.h"
#include "c8_DebugOut.h"
#include "keso_types.h"
#include "global.h"
#include "domains.h"


/*
 * call analysis 8 c30_DebugOutPrintStream_m6_println
 *
 * c7_HelloWorld_m1__init_
 * (valid java/io/PrintStream, "HelloWorld constructor
" java/lang/String)
 *
 * c7_HelloWorld_m2_run
 * (valid java/io/PrintStream, ?null java/lang/String)
 *
 * c7_HelloWorld_m2_run
 * (valid java/io/PrintStream, "You successfully compiled and ran KESO. Goodbye...
" java/lang/String)
 *
 * c7_HelloWorld_m2_run
 * (valid java/io/PrintStream, "m2" java/lang/String)
 *
 * c7_HelloWorld_m2_run
 * (valid java/io/PrintStream, ?null java/lang/String)
 *
 * c7_HelloWorld_m2_run
 * (valid java/io/PrintStream, ?null java/lang/String)
 *
 * c7_HelloWorld_m2_run
 * (valid java/io/PrintStream, ?null java/lang/String)
 *
 * c16_A_m1_m1
 * (valid java/io/PrintStream, "m1" java/lang/String)
 *
 * total (valid java/io/PrintStream, ?null java/lang/String)
 */

/* c30_DebugOutPrintStream_m6_println #non_blocking */
/* keso/io/DebugOutPrintStream.println(Ljava/lang/String;)V */

void c30_DebugOutPrintStream_m6_println(object_pointer obj0, object_pointer obj1)
{
	
/* c30_DebugOutPrintStream_m6_println_B0:  Pred:  No: 1 done */
	
/*==============================================================/
| 81:   DebugOut.println(s);
| 82:  }
/==============================================================*/

	c8_DebugOut_m6_println(obj1);
	/* goto c30_DebugOutPrintStream_m6_println_B6 */

	
/* c30_DebugOutPrintStream_m6_println_B6:  Pred:  0 No: 2 done */

	return;

}
