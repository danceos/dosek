/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#include "c25_System.h"
#include "c30_DebugOutPrintStream.h"
#include "keso_types.h"
#include "global.h"
#include "domains.h"


/*
 * call analysis 2 c25_System_m3__clinit_
 *
 * <kore>
 * ()
 *
 * <kore>
 * ()
 *
 * total ()
 */

/* c25_System_m3__clinit_ #non_blocking */
/* java/lang/System.<clinit>()V */

void c25_System_m3__clinit_(void)
{
	object_pointer obj1_0;
	
/* c25_System_m3__clinit__B0:  Pred:  No: 1 done */
	
/*==============================================================/
| 41:    out = err = new DebugOutPrintStream();
/==============================================================*/

	obj1_0 = KESO_ALLOC_C30_DEBUGOUTPRINTSTREAM();
	SC25_SYSTEM_C25F2_OUT(((domain_t *) &__DOSEK_APPDATA_dom1__DDesc)) = (object_pointer)obj1_0;
	/* goto c25_System_m3__clinit__B46 */

	
/* c25_System_m3__clinit__B46:  Pred:  0 No: 5 done */
	
/*==============================================================/
: 42:   } else {
: 43:    out = err = new NullPrintStream();
: 44:   }
| 45:  }
/==============================================================*/

	return;

}
