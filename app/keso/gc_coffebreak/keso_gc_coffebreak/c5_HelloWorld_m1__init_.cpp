/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#include "c5_HelloWorld.h"
#include "keso_types.h"
#include "global.h"
#include "domains.h"


/*
 * call analysis 1 c5_HelloWorld_m1__init_
 *
 * <kore>
 * ()
 *
 * total ()
 */

/* c5_HelloWorld_m1__init_ #non_blocking */
/* test/HelloWorld.<init>()V */

void c5_HelloWorld_m1__init_(object_pointer obj0)
{
	
/* c5_HelloWorld_m1__init__B0:  Pred:  No: 1 done */
	
/*==============================================================/
| 30:  private int runs = 0;
/==============================================================*/

	(ACCFIELD_C5_HELLOWORLD_C5F1_RUNS(obj0)) = (jint)(0);
	/* goto c5_HelloWorld_m1__init__B11 */

	
/* c5_HelloWorld_m1__init__B11:  Pred:  0 No: 3 done */

	return;

}

