/* THIS FILE IS AUTO-GENERATED BY KESO! DON'T EDIT */

#ifndef __DOMAINS_H__
#define __DOMAINS_H__
#include "keso_object_pointer.h"
#include "keso_static_fields.h"
#include "keso_types.h"
#include "global.h"


#define KESO_NUM_JAVADOMAINS 1
#include "coffee.h"

#define DOMAIN_DESC_BASEFIELDS \
	object_pointer  static_ref[KESO_NUM_STATIC_REFS];\
	const unsigned int heap_size;\
	unsigned int heap_free;\
	unsigned char colorbit;\

struct DOMAINDESC {
	DOMAIN_DESC_BASEFIELDS
} ATTR_MAYALIAS;
typedef struct DOMAINDESC domain_t;
struct domain_coffee_t {
	DOMAIN_DESC_BASEFIELDS
	struct {
		keso_gc_slotcnt_t sasls;
		unsigned char slotSize;
		coffee_listel_t* heap_top;
		coffee_listel_t* freemem;
	} hd;
};
#define DOMAIN_ZERO NULL
#define KESO_CURRENT_DOMAIN (((domain_t *) &__DOSEK_APPDATA_dom1__DDesc))
#define KESO_CURRENT_DOMAIN_GET_ENC KESO_CURRENT_DOMAIN
#define KESO_CURRENT_DOMAIN_GET KESO_CURRENT_DOMAIN
#include "coffee.h"

#define KESO_ALLOC(_cls_,_size_,_roff_) keso_coffee_alloc(_cls_,_size_,_roff_)
obj_size_t keso_objSize(obj_size_t slot_size, object_pointer obj);

#define keso_allocObject(ID) KESO_ALLOC(ID, CLS_SIZE(ID), CLS_ROFF(ID))
/* #define KESO_GCRun (_not_defined_) */
extern struct domain_coffee_t __DOSEK_APPDATA_dom1__DDesc;
extern char __DOSEK_APPDATA_dom1__heap[1024];



#endif /* !defined(__DOMAINS_H__) */
