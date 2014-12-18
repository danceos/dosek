#ifndef __keso_parity_h__
#define __keso_parity_h__ 1

/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/***********************************************************
 * Generated from c-templates/CodeTemplate/parity/parity.c *
 ***********************************************************/
/*
 * common parity utility
 */
#define KESO_GET_PARITY4_CONSTEXPR(x)  ((0x6996 >> ((x) & 0xf)) & 1)
#define KESO_GET_PARITY8_CONSTEXPR(x)  KESO_GET_PARITY4_CONSTEXPR((x)  ^ ((x) >> 4))
#define KESO_GET_PARITY16_CONSTEXPR(x) KESO_GET_PARITY8_CONSTEXPR((x)  ^ ((x) >> 8))
#define KESO_GET_PARITY32_CONSTEXPR(x) KESO_GET_PARITY16_CONSTEXPR((x) ^ ((x) >> 16))
#define KESO_GET_PARITY_CONSTEXPR(x)   KESO_GET_PARITY32_CONSTEXPR(x)

#if defined(__GNUC__)
	#define KESO_GET_PARITY32(x) __builtin_parity( (unsigned int) x)
	#define KESO_GET_PARITY16(x) __builtin_parity( (unsigned int) x) /*__builtin_parity(((unsigned int)x)&0xffff)*/
	#define KESO_GET_PARITY8(x)  __builtin_parity( (unsigned int) x) /*__builtin_parity(((unsigned int)x)&0xff)*/
	#define KESO_GET_PARITY4(x)  __builtin_parity(((unsigned int) x) & 0xf)
#else /* defined(__GNUC__) */
	#define KESO_GET_PARITY4(x)  KESO_GET_PARITY4_CONSTEXPR(x)
	#define KESO_GET_PARITY8(x)  keso_get_parity8(x)
	#define KESO_GET_PARITY16(x) keso_get_parity16(x)
	#define KESO_GET_PARITY32(x) keso_get_parity32(x)

	static inline unsigned int keso_get_parity8(unsigned int x) {
		return KESO_GET_PARITY4( (x) ^ ((x) >> 4));
	}
	static inline unsigned int keso_get_parity16(unsigned int x) {
		return KESO_GET_PARITY8( (x) ^ ((x) >> 8));
	}
	static inline unsigned int keso_get_parity32(unsigned int x) {
		return KESO_GET_PARITY16((x) ^ ((x) >> 16));
	}
#endif /* defined(__GNUC__) */

#define KESO_GET_PARITY(x) KESO_GET_PARITY32(x)

#if defined(__GNUC__)
	#define KESO_POPCOUNT(x) __builtin_popcount((unsigned int) x)
#else
	#define KESO_POPCOUNT(x) keso_popcount((unsigned int) x)

	static inline int keso_popcount(uint32_t i) {
		i = i - ((i >> 1) & 0x55555555);
		i = (i & 0x33333333) + ((i >> 2) & 0x33333333);
		return (((i + (i >> 4)) & 0x0F0F0F0F) * 0x01010101) >> 24;
	}
#endif
/**********************************************************************
 * Generated from c-templates/CodeTemplate/parity/parity_chk_common.c *
 **********************************************************************/
#include "keso_config_flags.h"
#include "keso_count_checks.h"
#include "keso_types.h"

#if defined(KESO_USE_CODED_REFS)\
	|| defined(KESO_USE_CODED_REFS_ON_GET_SET)\
	|| defined(KESO_USE_CODED_REFS_DOM)\
	|| defined(KESO_CODED_REF_CXXP_PARITY)

	#define KESO_PARITY_CHK_NEEDS_PINT 1
	
#endif

#if defined(KESO_PARITY_CHK_NEEDS_PINT)\
	|| defined(KESO_USE_CODED_REFS_HEADER_CHECK)\
	|| defined(KESO_USE_CODED_REFS_CHECK_ARRAYLENGTH)
	
	#define KESO_PARITY_CHK_REQUIRED 1

#endif

#ifdef KESO_COUNT_CHECKS
	extern int cnt_h;
	extern int cnt_r;
	extern int cnt_ah;
#endif

#ifdef KESO_PRODUCTION
	void keso_throw_error(void);
	#define keso_throw_parity(_where_,_method_,_bcpos_, obj) keso_throw_error()
#else /* defined(KESO_PRODUCTION) */
	void keso_throw_parity(const char *reason, const char* method, int bcpos, const void* obj);
#endif /* defined(KESO_PRODUCTION) */

/********************************************************************
 * Generated from c-templates/CodeTemplate/parity/parity_chk_pint.c *
 ********************************************************************/
/*using parity_chk_common.c*/

/*
	parity encoding, decoding and checking
	for pointers to data aligned at 4 byte boundaries ("int").
	the second least significant bit is used to establish an even parity.
*/

#ifdef KESO_PARITY_CHK_NEEDS_PINT

	 uintptr_t keso_add_parity_pint(void *_obj);
	 void keso_set_parity_pint(void **_obj);
	
	#define KESO_DECODE_PINT(_obj) ((uintptr_t) (_obj) & ~(1 << 1))
	#define KESO_ADD_PARITY_PINT keso_add_parity_pint
	#define KESO_SET_PARITY_PINT(_obj) keso_set_parity_pint((void**)&(_obj))
	
	
	#ifdef KESO_PRODUCTION
		#define KESO_PARITY_CHK_PINT_EXCEPTION_PARAMS
		#define KESO_PARITY_CHK_PINT_EXCEPTION_ARGS
		#define KESO_CHECK_PARITY_PINT(_obj, _method_, _bcpos_, _chkid_) keso_check_parity_pint(_obj)
		#define KESO_CHECK_AND_DECODE_PINT(_obj, _method_, _bcpos_, _chkid_) keso_check_and_decode_pint(_obj)
	#else
		#define KESO_PARITY_CHK_PINT_EXCEPTION_PARAMS ,const char *_method_, int _bcpos_, int _chkid_
		#define KESO_PARITY_CHK_PINT_EXCEPTION_ARGS ,_method_, _bcpos_, _chkid_
		#define KESO_CHECK_PARITY_PINT(_obj, _method_, _bcpos_, _chkid_) keso_check_parity_pint(_obj, _method_, _bcpos_, _chkid_)
		#define KESO_CHECK_AND_DECODE_PINT(_obj, _method_, _bcpos_, _chkid_) keso_check_and_decode_pint(_obj, _method_, _bcpos_, _chkid_)
	#endif
	
	
	 void *keso_check_parity_pint(void *_obj KESO_PARITY_CHK_PINT_EXCEPTION_PARAMS);
	 uintptr_t keso_check_and_decode_pint(void *_obj_ KESO_PARITY_CHK_PINT_EXCEPTION_PARAMS);

#endif

/******************************************************************
 * Generated from c-templates/CodeTemplate/parity/parity_chk_hc.c *
 ******************************************************************/
#include "keso_config_flags.h"
#include "keso_count_checks.h"
#include "keso_object.h"

/* using parity_chk_common.c */

/********   header en-/decoding   ********/
#ifndef KESO_USE_CODED_REFS_HEADER_CHECK
	#define KESO_DECODE_HEADER_CHECKCAST(obj, _method_) ((obj)->class_id)
	#define KESO_INIT_PARITY_HEADER(obj) ((void)(obj))
	#define KESO_DECODE_HEADER(obj,method) ((obj)->class_id)
#else
	/* TODO replace MagicNumbers "3" and "4": Avoid conflicts with other flags stored in gcinfo */
	#define KESO_CLASS_ID_PARITY_BIT_SHIFT 3
	#define KESO_CLASS_ID_PARITY_BIT (1 << KESO_CLASS_ID_PARITY_BIT_SHIFT)

	#define KESO_INIT_PARITY_HEADER(obj) keso_init_parity_header(obj)
	#define KESO_DECODE_HEADER(obj,method) keso_decode_header(obj,method)

	 void keso_init_parity_header(object_t *obj);
	 class_id_t keso_decode_header(const object_t *obj, const char *_method_);

	#ifdef KESO_USE_CODED_REFS_HEADER_CHECK_NO_CHECKCAST
		#define KESO_DECODE_HEADER_CHECKCAST(obj, _method_) \
			((obj)->class_id)
	#else
		#define KESO_DECODE_HEADER_CHECKCAST(obj, _method_) \
			KESO_DECODE_HEADER(obj, _method_)
	#endif
#endif


/********   arraylength en-/decoding   ********/
#ifndef KESO_USE_CODED_REFS_CHECK_ARRAYLENGTH
	#define KESO_CHECK_AND_DECODE_ARRAYLENGTH(obj, _method_, _bcpos_, _chkid_) (((const array_t*)(obj))->size)
	#ifdef PROGMEM
		#define KESO_CHECK_AND_DECODE_ARRAYLENGTH_PGM(obj, _method_, _bcpos_, _chkid_) pgm_read_byte(&((const array_t *) (obj))->size)
	#endif
	#define KESO_ADD_PARITY_ARRAYLENGTH(obj) ((object_t*)(obj))
#else
	/*TODO replace MagicNumbers "3" and "4": Avoid conflicts with other flags stored in gcinfo*/
	#define KESO_ARRAYLENGTH_PARITY_BIT_SHIFT 4
	#define KESO_ARRAYLENGTH_PARITY_BIT (1 << KESO_ARRAYLENGTH_PARITY_BIT_SHIFT)

	#define KESO_CHECK_AND_DECODE_ARRAYLENGTH(obj, _method_, _bcpos_, _chkid_) \
			keso_check_and_decode_arraylength((array_t *) (obj), _method_, _bcpos_, _chkid_)

	#define KESO_ADD_PARITY_ARRAYLENGTH(obj) \
			keso_add_parity_arraylength((array_t *) (obj))

	 array_size_t keso_check_and_decode_arraylength(const array_t *obj, const char *_method_, int _bcpos_, int _chkid_);
	 object_t *keso_add_parity_arraylength(array_t *obj);
#endif
#define KESO_SET_PARITY_ARRAYLENGTH(obj) ((void)KESO_ADD_PARITY_ARRAYLENGTH(obj))
#ifdef KESO_MAGIC_VALUE_HEADER
#define KESO_OBJECT_HEADER_MAGIC_VALUE 0xa5
#endif
/********************************************************************
 * Generated from c-templates/CodeTemplate/parity/parity_chk_refs.c *
 ********************************************************************/
#include "keso_object.h"

/*using parity_chk_pint.c*/

#ifdef KESO_PARITY_CHK_NEEDS_PINT
	#define NATIVE_ADDR_EXPLICIT(_obj) ((object_t *)KESO_DECODE_PINT(_obj))
#else
	#define NATIVE_ADDR_EXPLICIT(_obj) (_obj)
#endif
	/*
		NATIVE_ADDR_EXPLICIT will always decode the passed reference
			(if there is an encoding).
		NATIVE_ADDR will decode the passed reference, if all references -even
		local variables- are permanently encoded.
		NATIVE_ADDR_RETURN will decode the reference, if local variables are
		required to be in native form.
	*/
#ifdef KESO_USE_CODED_REFS_ON_GET_SET
	#define NATIVE_ADDR(_obj) (_obj)
	#define NATIVE_ADDR_RETURN(_obj) NATIVE_ADDR_EXPLICIT(_obj)
#elif defined(KESO_USE_CODED_REFS)
	#define NATIVE_ADDR(_obj) NATIVE_ADDR_EXPLICIT(_obj)
	#define NATIVE_ADDR_RETURN(_obj) (_obj)
#else
	#define NATIVE_ADDR(_obj) (_obj)
	#define NATIVE_ADDR_RETURN(_obj) (_obj)
#endif

/********   reference en-/decoding   ********/
#if defined(KESO_USE_CODED_REFS) || defined(KESO_USE_CODED_REFS_ON_GET_SET)

	#define SET_PARITY(_obj) KESO_SET_PARITY_PINT(_obj)
	#define ADD_PARITY(_obj) ((object_t*)KESO_ADD_PARITY_PINT((void *) ( _obj)))
	#define KESO_CHECK_PARITY(_obj, _method_, _bcpos_, _chkid_)\
		KESO_CHECK_PARITY_PINT(_obj, _method_, _bcpos_, _chkid_)

	#define KESO_CHECK_AND_DECODE_REFERENCE(_obj, _method_, _bcpos_, _chkid_) \
		((object_t *)KESO_CHECK_AND_DECODE_PINT(_obj, _method_, _bcpos_, _chkid_))
			
#else
	#define SET_PARITY(_obj) ((void)(_obj))
	#define ADD_PARITY(_obj) ((object_t*)(_obj))
	#define KESO_CHECK_AND_DECODE_REFERENCE(_obj, _method_, _bcpos_, _chkid_) ((object_t*)(_obj))
	#define KESO_CHECK_PARITY(_obj, _method_, _bcpos_, _chkid_) ((object_t*)(_obj))
#endif

/********   instruction parity check get set macros   ********/
/*
	use_coded_refs_no_fields: Do not encode instance-fields
	use_coded_refs_no_arrays: Do not encode array-fields	
	use_coded_refs_no_static_fields: Do not encode static fields
*/

#ifdef USE_CODED_REFS_NO_FIELDS
	#define KESO_CHECK_AND_DECODE_REFERENCE_GETFIELD(_obj, _method_, _bcpos_, _chkid_) ((object_t*)(_obj))
	#define KESO_ADD_PARITY_PUTFIELD(_obj)  ((object_t*)(_obj))
#else
	#define KESO_CHECK_AND_DECODE_REFERENCE_GETFIELD(_obj, _method_, _bcpos_, _chkid_) \
			KESO_CHECK_AND_DECODE_REFERENCE(_obj, _method_, _bcpos_, _chkid_)
	#define KESO_ADD_PARITY_PUTFIELD(_obj)  ADD_PARITY(_obj)
#endif

#ifdef USE_CODED_REFS_NO_ARRAYS
	#define KESO_CHECK_AND_DECODE_REFERENCE_AALOAD(_obj, _method_, _bcpos_, _chkid_) ((object_t*)(_obj))
	#define KESO_ADD_PARITY_AASTORE(_obj)   ((object_t*)(_obj))
#else
	#define KESO_CHECK_AND_DECODE_REFERENCE_AALOAD(_obj, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_AND_DECODE_REFERENCE(_obj, _method_, _bcpos_, _chkid_)
	#define KESO_ADD_PARITY_AASTORE(_obj)   ADD_PARITY(_obj)
#endif

#ifdef USE_CODED_REFS_NO_STATIC_FIELDS
	#define KESO_CHECK_AND_DECODE_REFERENCE_GETSTATIC(_obj, _method_, _bcpos_, _chkid_) ((object_t*)(_obj))
	#define KESO_ADD_PARITY_PUTSTATIC(_obj) ((object_t*)(_obj))
#else
	#define KESO_CHECK_AND_DECODE_REFERENCE_GETSTATIC(_obj, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_AND_DECODE_REFERENCE(_obj, _method_, _bcpos_, _chkid_)
	#define KESO_ADD_PARITY_PUTSTATIC(_obj) ADD_PARITY(_obj)
#endif

/*******************************************************************
 * Generated from c-templates/CodeTemplate/parity/parity_chk_dom.c *
 *******************************************************************/
/* using parity_chk_pint.c */
/********   domain-descriptor en-/decoding   ********/
#ifdef KESO_USE_CODED_REFS_DOM
	/*#include "domains.h"*/
	#define KESO_CHECK_AND_DECODE_DOM(dom) ((domain_t *)KESO_CHECK_AND_DECODE_PINT(dom,"keso_check_and_decode_domain",-1,-1))
	#define KESO_CHECK_PARITY_DOM(dom)     ((domain_t *)KESO_CHECK_PARITY_PINT(dom,"keso_check_parity_domain",-1,-1))
	#define KESO_ADD_PARITY_DOM(dom)       ((domain_t *)KESO_ADD_PARITY_PINT(dom))
	#define KESO_SET_PARITY_DOM(dom)       KESO_SET_PARITY_PINT(dom)
	#define KESO_DECODE_DOM(dom)           ((domain_t *)KESO_DECODE_PINT(dom))
#else
	#define KESO_CHECK_AND_DECODE_DOM(dom) ((domain_t *)(dom))
	#define KESO_CHECK_PARITY_DOM(dom)     ((domain_t *)(dom))
	#define KESO_ADD_PARITY_DOM(dom)       ((domain_t *)(dom))
	#define KESO_SET_PARITY_DOM(dom)       ((void)(dom))
	#define KESO_DECODE_DOM(dom)           ((domain_t *)(dom))
#endif
/********************************************************************
 * Generated from c-templates/CodeTemplate/parity/parity_chk_dref.c *
 ********************************************************************/
/*using parity_chk_ref.c*/

#if defined(KESO_USE_CODED_REFS)
	/********   instruction parity check macros   ********/
	#ifndef KESO_OMIT_CHECK_ARRAYLENGTH_PARITY
		#define KESO_CHECK_ARRAYLENGTH_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_ARRAYLENGTH_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_LALOAD_PARITY
		#define KESO_CHECK_LALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_LALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_LASTORE_PARITY
		#define KESO_CHECK_LASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_LASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_AGETFIELD_PARITY
		#define KESO_CHECK_AGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_AGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_APUTFIELD_PARITY
		#define KESO_CHECK_APUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_APUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_BALOAD_PARITY
		#define KESO_CHECK_BALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_BALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_BASTORE_PARITY
		#define KESO_CHECK_BASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_BASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_BGETFIELD_PARITY
		#define KESO_CHECK_BGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_BGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_BPUTFIELD_PARITY
		#define KESO_CHECK_BPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
			KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_BPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_CALOAD_PARITY
		#define KESO_CHECK_CALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_CALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_CASTORE_PARITY
		#define KESO_CHECK_CASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_CASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_CGETFIELD_PARITY
		#define KESO_CHECK_CGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_CGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_CPUTFIELD_PARITY
		#define KESO_CHECK_CPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
			KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_CPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_DALOAD_PARITY
		#define KESO_CHECK_DALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_DALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_DASTORE_PARITY
		#define KESO_CHECK_DASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_DASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_DGETFIELD_PARITY
		#define KESO_CHECK_DGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_DGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_DPUTFIELD_PARITY
		#define KESO_CHECK_DPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_DPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_FALOAD_PARITY
		#define KESO_CHECK_FALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_FALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_FASTORE_PARITY
		#define KESO_CHECK_FASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_FASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_FGETFIELD_PARITY
		#define KESO_CHECK_FGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_FGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_FPUTFIELD_PARITY
		#define KESO_CHECK_FPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_FPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_JGETFIELD_PARITY
		#define KESO_CHECK_JGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_JGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_JPUTFIELD_PARITY
		#define KESO_CHECK_JPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_JPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_IALOAD_PARITY
		#define KESO_CHECK_IALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_IALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_IASTORE_PARITY
		#define KESO_CHECK_IASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_IASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_IGETFIELD_PARITY
		#define KESO_CHECK_IGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_IGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_IPUTFIELD_PARITY
		#define KESO_CHECK_IPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_IPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_ZGETFIELD_PARITY
		#define KESO_CHECK_ZGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_ZGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_ZPUTFIELD_PARITY
		#define KESO_CHECK_ZPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_ZPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_JALOAD_PARITY
		#define KESO_CHECK_JALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_JALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_JASTORE_PARITY
		#define KESO_CHECK_JASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_JASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_LGETFIELD_PARITY
		#define KESO_CHECK_LGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_LGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_LPUTFIELD_PARITY
		#define KESO_CHECK_LPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_LPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_SALOAD_PARITY
		#define KESO_CHECK_SALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_SALOAD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_SASTORE_PARITY
		#define KESO_CHECK_SASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_SASTORE_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_SGETFIELD_PARITY
		#define KESO_CHECK_SGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_SGETFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_SPUTFIELD_PARITY
		#define KESO_CHECK_SPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_SPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_ZPUTFIELD_PARITY
		#define KESO_CHECK_ZPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_ZPUTFIELD_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_INVOKEINTERFACE_PARITY
		#define KESO_CHECK_INVOKEINTERFACE_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_INVOKEINTERFACE_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_INVOKESPECIAL_PARITY
		#define KESO_CHECK_INVOKESPECIAL_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_INVOKESPECIAL_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif


	#ifndef KESO_OMIT_CHECK_INVOKEVIRTUAL_PARITY
		#define KESO_CHECK_INVOKEVIRTUAL_PARITY(_obj_,_method_,_bcpos_, _chkid_) \
				KESO_CHECK_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#else
		#define KESO_CHECK_INVOKEVIRTUAL_PARITY(_obj_,_method_,_bcpos_, _chkid_)
	#endif
#endif /* defined(KESO_USE_CODED_REFS) */
#endif
