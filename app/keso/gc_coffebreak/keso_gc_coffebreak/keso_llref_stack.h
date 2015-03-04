#ifndef __keso_llref_stack_h__
#define __keso_llref_stack_h__

#include "keso_types.h"
#include "keso_object_pointer.h"


typedef struct keso_stack_s {
} keso_stack_t;

typedef struct keso_stack_simple_s {
	keso_stack_t super;
	struct DOMAINDESC *domain;
	object_pointer *llrefs;
	struct keso_stack_s *next;
} keso_stack_simple_t;

#define KESO_EOLL ((object_pointer) (void *) ~6) /* end of linked list */
#endif
