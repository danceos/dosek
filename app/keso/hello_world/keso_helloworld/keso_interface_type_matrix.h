#ifndef __keso_interface_type_matrix_h__
#define __keso_interface_type_matrix_h__ 1

/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/**************************************************************************************
 * Generated from c-templates/CodeTemplate/interfaceTypeMatrix/checkInterfaceCommon.c *
 **************************************************************************************/
#include "keso_config_flags.h"
#include "keso_object.h"

#define MAX_IFACE_ID (0)

#if MAX_IFACE_ID > 31
	#define KESO_INTERFACE_IDENTIFIER(x) (x)
#else /* MAX_IFACE_ID > 31 */
	#define KESO_INTERFACE_IDENTIFIER(x) (1 << (x))
#endif /* MAX_IFACE_ID > 31 */
/*************************************************************************************
 * Generated from c-templates/CodeTemplate/interfaceTypeMatrix/checkInterfaceMacro.c *
 *************************************************************************************/
#ifdef KESO_USE_CODED_REFS
#include "keso_parity.h"

	#define CHK_IFACE_ID33(_obj_) \
		keso_checkiface((object_pointer) (NATIVE_ADDR(_obj_)), KESO_INTERFACE_IDENTIFIER(0))
	#define INSTANCEOF_IFACE_ID33(_obj_) \
		keso_instanceof_iface((object_pointer) (NATIVE_ADDR(_obj_)), KESO_INTERFACE_IDENTIFIER(0))
#else /* defined(KESO_USE_CODED_REFS) */
	#define CHK_IFACE_ID33(_obj_) \
		keso_checkiface(_obj_, KESO_INTERFACE_IDENTIFIER(0))
	#define INSTANCEOF_IFACE_ID33(_obj_) \
		keso_instanceof_iface(_obj_, KESO_INTERFACE_IDENTIFIER(0))
#endif /* defined(KESO_USE_CODED_REFS) */
/*************************************************************************************
 * Generated from c-templates/CodeTemplate/interfaceTypeMatrix/checkInterfaceMacro.c *
 *************************************************************************************/
#ifdef KESO_USE_CODED_REFS
#include "keso_parity.h"

	#define CHK_IFACE_ID34(_obj_) \
		keso_checkiface((object_pointer) (NATIVE_ADDR(_obj_)), KESO_INTERFACE_IDENTIFIER(0))
	#define INSTANCEOF_IFACE_ID34(_obj_) \
		keso_instanceof_iface((object_pointer) (NATIVE_ADDR(_obj_)), KESO_INTERFACE_IDENTIFIER(0))
#else /* defined(KESO_USE_CODED_REFS) */
	#define CHK_IFACE_ID34(_obj_) \
		keso_checkiface(_obj_, KESO_INTERFACE_IDENTIFIER(0))
	#define INSTANCEOF_IFACE_ID34(_obj_) \
		keso_instanceof_iface(_obj_, KESO_INTERFACE_IDENTIFIER(0))
#endif /* defined(KESO_USE_CODED_REFS) */
/*************************************************************************************
 * Generated from c-templates/CodeTemplate/interfaceTypeMatrix/checkInterfaceMacro.c *
 *************************************************************************************/
#ifdef KESO_USE_CODED_REFS
#include "keso_parity.h"

	#define CHK_IFACE_ID35(_obj_) \
		keso_checkiface((object_pointer) (NATIVE_ADDR(_obj_)), KESO_INTERFACE_IDENTIFIER(0))
	#define INSTANCEOF_IFACE_ID35(_obj_) \
		keso_instanceof_iface((object_pointer) (NATIVE_ADDR(_obj_)), KESO_INTERFACE_IDENTIFIER(0))
#else /* defined(KESO_USE_CODED_REFS) */
	#define CHK_IFACE_ID35(_obj_) \
		keso_checkiface(_obj_, KESO_INTERFACE_IDENTIFIER(0))
	#define INSTANCEOF_IFACE_ID35(_obj_) \
		keso_instanceof_iface(_obj_, KESO_INTERFACE_IDENTIFIER(0))
#endif /* defined(KESO_USE_CODED_REFS) */
#endif
