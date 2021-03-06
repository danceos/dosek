/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#include "keso_types.h"
#include "global.h"
#include "domains.h"


#define KESO_ALIGN_OBJ(_size_) ((_size_+3)&~3)
#include "rds.h"
#include "keso_exceptions.h"

object_pointer keso_rds_alloc(class_id_t class_id, obj_size_t size, obj_size_t roff){

	char* mem;
	int i = KESO_ALIGN_OBJ(size);
	object_pointer obj;

	struct domain_rds_t* domain = (struct domain_rds_t *) KESO_CURRENT_DOMAIN_GET;

#ifdef KESO_GC_STATS
	domain->hd.gc_stats_allocs++;
#endif

	mem = domain->hd.new_ptr;
	domain->hd.new_ptr += i;

	if (domain->hd.new_ptr > domain->hd.heap_end){
		KESO_THROW_ERROR("out of memory");
	}

	domain->heap_free -= i;

#ifdef KESO_GC_STATS
	domain->hd.gc_stats_allocated_memory += i;
#endif

#ifdef KESO_IS_8BIT_CONTROLLER
	while(i-- > 0){
		mem[i] = 0;
	}
#else
	i /= sizeof(int);
	while(i-- > 0){
		((int *)mem)[i] = 0;
	}
#endif

	obj = (object_pointer ) ((object_pointer *)mem + roff);
	obj->class_id = class_id;

#if defined KESO_RECOVERY || defined KESO_USE_CODED_REFS_HEADER_CHECK
	/* mark object for heap scan */
	obj->gcinfo = 1;
#endif

#ifdef KESO_USE_CODED_REFS_HEADER_CHECK
	KESO_INIT_PARITY_HEADER(obj);
#endif

	return obj;

}


