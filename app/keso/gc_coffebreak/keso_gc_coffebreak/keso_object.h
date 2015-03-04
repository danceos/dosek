#ifndef __keso_object_h__
#define __keso_object_h__

#include "keso_types.h"
#include "keso_compiler_extensions.h"

typedef int keso_machineword_t;
typedef unsigned int keso_umachineword_t;
typedef unsigned short	class_id_t;
typedef unsigned int	array_size_t;
#define OBJECT_HEADER \
	unsigned char	gcinfo;\
	class_id_t	class_id;\

typedef struct object_t {
	/* size = 4, align = 2 */
	unsigned char	gcinfo;	/* from "object_t" (o:0,s:1,a:1)*/
	class_id_t	class_id;	/* from "object_t" (o:2,s:2,a:2)*/
} object_t;

#define ARRAY_HEADER \
	unsigned char	gcinfo;\
	class_id_t	class_id;\
	array_size_t	size;\

typedef struct array_t {
	/* size = 8, align = 4 */
	unsigned char	gcinfo;	/* from "object_t" (o:0,s:1,a:1)*/
	class_id_t	class_id;	/* from "object_t" (o:2,s:2,a:2)*/
	array_size_t	size;	/* from "array_t" (o:4,s:4,a:4)*/
} array_t;

typedef unsigned int   obj_size_t;

#endif
