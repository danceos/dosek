#ifndef __keso_exceptions_h__
#define __keso_exceptions_h__ 1

/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/******************************************************************
 * Generated from c-templates/CodeTemplate/exceptions/array_chk.c *
 ******************************************************************/
#include "keso_config_flags.h"
#include "keso_count_checks.h"
#include "keso_parity.h"
#include "keso_types.h"

#ifdef KESO_OMIT_SAFECHECKS
	#define KESO_CHECK_ARRAY_NOTNULL(_obj_,_index_,_method_,_bcpos_, _chkid_)
	#ifdef PROGMEM
		#define KESO_CHECK_ARRAY_NOTNULL_PGM(_obj_, _index_, _method_, _bcpos_, _chkid_)
	#endif
	#define KESO_CHECK_ARRAY_KNOWNBOUNDS(_m_size_, _a_size_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_BOUNDS(_clazz_, _mem_, _a_size_, _method_, _bcpos_, _chkid_)
#else /* defined(KESO_OMIT_SAFECHECKS) */
	/* Decode the length of an array if necessary (see parity_chk.c) */
	#define KESO_CHECK_ARRAY_NOTNULL(_obj_,_index_,_method_,_bcpos_, _chkid_) \
		KESO_COUNT_CHECK(_chkid_); \
		if (unlikely(KESO_CHECK_AND_DECODE_ARRAYLENGTH(NATIVE_ADDR(_obj_),_method_,_bcpos_,_chkid_) <= (array_size_t) _index_)) \
			keso_throw_index_out_of_bounds(_method_, _bcpos_);

	#ifdef PROGMEM
		#define KESO_CHECK_ARRAY_NOTNULL_PGM(_obj_, _index_, _method_, _bcpos_, _chkid_) \
			KESO_COUNT_CHECK(_chkid_); \
			if (unlikely(KESO_CHECK_AND_DECODE_ARRAYLENGTH_PGM(NATIVE_ADDR(_obj_),_method_,_bcpos_,_chkid_) <= (array_size_t) _index_)) \
				keso_throw_index_out_of_bounds(_method_, _bcpos_);
	#endif

	/* constant bounds check for known sizes */
	#define KESO_CHECK_ARRAY_KNOWNBOUNDS(_m_size_, _a_size_, _method_, _bcpos_, _chkid_)\
		KESO_COUNT_CHECK(_chkid_); \
		if (unlikely((array_size_t)(_a_size_)>=(array_size_t)(_m_size_)))\
			keso_throw_index_out_of_bounds(_method_,_bcpos_)

	/* bounds check for non-null _mem_ memory object */
	#define KESO_CHECK_BOUNDS(_clazz_, _mem_, _a_size_, _method_, _bcpos_, _chkid_)\
		KESO_COUNT_CHECK(_chkid_); \
		if (unlikely((_a_size_)>=((_clazz_*)_mem_)->_size)) \
			keso_throw_index_out_of_bounds(_method_,_bcpos_)
#endif /* defined(KESO_OMIT_SAFECHECKS) */

#ifdef KESO_PRODUCTION
	#define keso_throw_index_out_of_bounds(_method_,_bcpos_) keso_throw_error()
#else
	void keso_throw_index_out_of_bounds(const char* method, int bcpos);
#endif
/***********************************************************************
 * Generated from c-templates/CodeTemplate/exceptions/array_chk_insn.c *
 ***********************************************************************/
/********   instruction specific array check macros   ********/
#ifdef KESO_OMIT_CHECK_ARRAYLENGTH_ARRAY
	#define KESO_CHECK_ARRAYLENGTH_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_ARRAYLENGTH_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_ARRAYLENGTH_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_ARRAYLENGTH_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_ARRAYLENGTH_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_ARRAYLENGTH_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAYLENGTH_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_ARRAYLENGTH_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_LALOAD_ARRAY
	#define KESO_CHECK_LALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_LALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_LALOAD_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_LALOAD_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_LALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_LALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_LALOAD_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_LALOAD_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_LASTORE_ARRAY
	#define KESO_CHECK_LASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_LASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_LASTORE_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_LASTORE_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_LASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_LASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_LASTORE_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_LASTORE_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_BALOAD_ARRAY
	#define KESO_CHECK_BALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_BALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_BALOAD_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_BALOAD_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_BALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_BALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_BALOAD_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_BALOAD_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_BASTORE_ARRAY
	#define KESO_CHECK_BASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_BASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_BASTORE_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_BASTORE_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_BASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_BASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_BASTORE_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_BASTORE_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_CALOAD_ARRAY
	#define KESO_CHECK_CALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_CALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_CALOAD_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_CALOAD_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_CALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_CALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_CALOAD_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_CALOAD_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_CASTORE_ARRAY
	#define KESO_CHECK_CASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_CASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_CASTORE_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_CASTORE_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_CASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_CASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_CASTORE_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_CASTORE_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_DALOAD_ARRAY
	#define KESO_CHECK_DALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_DALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_DALOAD_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_DALOAD_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_DALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_DALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_DALOAD_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_DALOAD_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_DASTORE_ARRAY
	#define KESO_CHECK_DASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_DASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_DASTORE_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_DASTORE_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_DASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_DASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_DASTORE_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_DASTORE_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_FALOAD_ARRAY
	#define KESO_CHECK_FALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_FALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_FALOAD_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_FALOAD_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_FALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_FALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_FALOAD_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_FALOAD_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_FASTORE_ARRAY
	#define KESO_CHECK_FASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_FASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_FASTORE_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_FASTORE_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_FASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_FASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_FASTORE_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_FASTORE_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_IALOAD_ARRAY
	#define KESO_CHECK_IALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_IALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_IALOAD_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_IALOAD_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_IALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_IALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_IALOAD_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_IALOAD_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_IASTORE_ARRAY
	#define KESO_CHECK_IASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_IASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_IASTORE_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_IASTORE_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_IASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_IASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_IASTORE_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_IASTORE_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_JALOAD_ARRAY
	#define KESO_CHECK_JALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_JALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_JALOAD_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_JALOAD_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_JALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_JALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_JALOAD_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_JALOAD_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_JASTORE_ARRAY
	#define KESO_CHECK_JASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_JASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_JASTORE_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_JASTORE_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_JASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_JASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_JASTORE_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_JASTORE_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_SALOAD_ARRAY
	#define KESO_CHECK_SALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_SALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_SALOAD_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_SALOAD_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_SALOAD_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_SALOAD_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_SALOAD_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_SALOAD_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif

#ifdef KESO_OMIT_CHECK_SASTORE_ARRAY
	#define KESO_CHECK_SASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_SASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_SASTORE_ARRAY_KNOWNBOUNDS(_bound_,_index_, _method_,_bcpos_, _chkid_)
#else
	#define KESO_CHECK_SASTORE_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_KNOWNBOUNDS(_bound_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_SASTORE_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_ARRAY_NOTNULL(_arr_, _index_, _method_, _bcpos_, _chkid_)
	#define KESO_CHECK_SASTORE_ARRAY(_arr_, _index_, _method_, _bcpos_, _chkid_) \
		KESO_CHECK_SASTORE_NULLPOINTER(_arr_, _method_, _bcpos_, _chkid_); \
		KESO_CHECK_SASTORE_ARRAY_NOTNULL(_arr_,_index_,_method_,_bcpos_, _chkid_);
#endif
/**********************************************************************
 * Generated from c-templates/CodeTemplate/exceptions/arraysize_chk.c *
 **********************************************************************/
#include "keso_config_flags.h"
#include "keso_count_checks.h"

#ifdef KESO_OMIT_SAFECHECKS
	#define KESO_CHECK_ARRAYSIZE(_size_, _method_, _bcpos_, _chkid_)
#else
	#define KESO_CHECK_ARRAYSIZE(_size_, _method_, _bcpos_, _chkid_) \
		KESO_COUNT_CHECK(_chkid_); \
		if (unlikely((int) _size_ < 0)) \
			keso_throw_negative_array_size(_method_, _bcpos_);
	#ifdef KESO_PRODUCTION
		#define keso_throw_negative_array_size(_method_, _bcpos_) keso_throw_error()
	#else
		void keso_throw_negative_array_size(const char* method, int bcpos);
	#endif
#endif
/******************************************************************
 * Generated from c-templates/CodeTemplate/exceptions/error_chk.c *
 ******************************************************************/
#include "keso_config_flags.h"

#if !defined(KESO_PRODUCTION) && defined(KESO_LLCALLSTACK)
	#include "keso_llcallstack.h"
	#define KESO_PRINT_STACKTRACE KESO_LLCALLSTACK_PRINT
#else
	#define KESO_PRINT_STACKTRACE() ((void) 0)
#endif

#ifdef KESO_PRODUCTION
	#define KESO_THROW_ERROR(_msg_) keso_throw_error()
	void NORETURN keso_throw_error(void);
#else /* defined(KESO_PRODUCTION) */
	#define KESO_THROW_ERROR(_msg_) keso_throw_error(_msg_)
	void NORETURN keso_throw_error(const char *msg);
#endif /* defined(KESO_PRODUCTION) */

#ifdef DEBUG
	#define QUOTE(X) QUOTE2(X)
	#define QUOTE2(X) #X
	#define KESO_ASSERT(__v__) \
		if (!(__v__)) \
			KESO_THROW_ERROR("Assertion failed in " __FILE__ ":" QUOTE(__LINE__))
	#define KESO_ASSERT_MSG(__v__, MSG) \
		if (!(__v__)) \
			KESO_THROW_ERROR("Assertion failed in " __FILE__ ":" QUOTE(__LINE__) ": " MSG)
#else /* defined(DEBUG) */
	#define KESO_ASSERT(__v__)
	#define KESO_ASSERT_MSG(__v__, MSG)
#endif /* defined(DEBUG) */
/*****************************************************************
 * Generated from c-templates/CodeTemplate/exceptions/null_chk.c *
 *****************************************************************/
/*#include "global.h"*/
#include "keso_config_flags.h"
#include "keso_compiler_extensions.h"
#include "keso_count_checks.h"
#include "keso_object_pointer.h"

void keso_check_obj(object_pointer obj);

#define KESO_ASSERT_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) KESO_ASSERT((_obj_) != (object_pointer) (void *) 0)

#ifdef KESO_OMIT_SAFECHECKS
#	define KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	ifdef KESO_USE_CODED_REFS
#		define KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) KESO_COUNT_CHECK(_chkid_); if (unlikely(((object_pointer) (void *) 0)==(NATIVE_ADDR(_obj_)))) keso_throw_nullpointer(_method_,_bcpos_);
#	else
#		define KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) KESO_COUNT_CHECK(_chkid_); if (unlikely(((object_pointer) (void *) 0)==(_obj_))) keso_throw_nullpointer(_method_,_bcpos_);
#	endif

#	ifdef KESO_PRODUCTION
#		define keso_throw_nullpointer(_method_,_bcpos_) keso_throw_error()
#	else
		void keso_throw_nullpointer(const char* method, int bcpos);
#	endif
#endif

/********   pseudo instruction specific null check macros   ********/
#ifndef KESO_OMIT_CHECK_MEMBOUNDS_NULLPOINTER
#	define KESO_CHECK_MEMBOUNDS_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_MEMBOUNDS_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_MEMLOAD_NULLPOINTER
#	define KESO_CHECK_MEMLOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_MEMLOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_MEMSTORE_NULLPOINTER
#	define KESO_CHECK_MEMSTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_MEMSTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_MGETFIELD_NULLPOINTER
#	define KESO_CHECK_MGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_MGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_MPUTFIELD_NULLPOINTER
#	define KESO_CHECK_MPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_MPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

/********   instruction specific null check macros   ********/
#ifndef KESO_OMIT_CHECK_ARRAYLENGTH_NULLPOINTER
#	define KESO_CHECK_ARRAYLENGTH_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_ARRAYLENGTH_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_LALOAD_NULLPOINTER
#	define KESO_CHECK_LALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_LALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_LASTORE_NULLPOINTER
#	define KESO_CHECK_LASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_LASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_AGETFIELD_NULLPOINTER
#	define KESO_CHECK_AGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_AGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_APUTFIELD_NULLPOINTER
#	define KESO_CHECK_APUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_APUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_BALOAD_NULLPOINTER
#	define KESO_CHECK_BALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_BALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_BASTORE_NULLPOINTER
#	define KESO_CHECK_BASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_BASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_BGETFIELD_NULLPOINTER
#	define KESO_CHECK_BGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_BGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_BPUTFIELD_NULLPOINTER
#	define KESO_CHECK_BPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_BPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_CALOAD_NULLPOINTER
#	define KESO_CHECK_CALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_CALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_CASTORE_NULLPOINTER
#	define KESO_CHECK_CASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_CASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_CGETFIELD_NULLPOINTER
#	define KESO_CHECK_CGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_CGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_CPUTFIELD_NULLPOINTER
#	define KESO_CHECK_CPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_CPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_DALOAD_NULLPOINTER
#	define KESO_CHECK_DALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_DALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_DASTORE_NULLPOINTER
#	define KESO_CHECK_DASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_DASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_DGETFIELD_NULLPOINTER
#	define KESO_CHECK_DGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_DGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_DPUTFIELD_NULLPOINTER
#	define KESO_CHECK_DPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_DPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_FALOAD_NULLPOINTER
#	define KESO_CHECK_FALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_FALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_FASTORE_NULLPOINTER
#	define KESO_CHECK_FASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_FASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_FGETFIELD_NULLPOINTER
#	define KESO_CHECK_FGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_FGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_FPUTFIELD_NULLPOINTER
#	define KESO_CHECK_FPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_FPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_JGETFIELD_NULLPOINTER
#	define KESO_CHECK_JGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_JGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_JPUTFIELD_NULLPOINTER
#	define KESO_CHECK_JPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_JPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_IALOAD_NULLPOINTER
#	define KESO_CHECK_IALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_IALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_IASTORE_NULLPOINTER
#	define KESO_CHECK_IASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_IASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_IGETFIELD_NULLPOINTER
#	define KESO_CHECK_IGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_IGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_IPUTFIELD_NULLPOINTER
#	define KESO_CHECK_IPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_IPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_ZGETFIELD_NULLPOINTER
#	define KESO_CHECK_ZGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_ZGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_ZPUTFIELD_NULLPOINTER
#	define KESO_CHECK_ZPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_ZPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_JALOAD_NULLPOINTER
#	define KESO_CHECK_JALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_JALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_JASTORE_NULLPOINTER
#	define KESO_CHECK_JASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_JASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_LGETFIELD_NULLPOINTER
#	define KESO_CHECK_LGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_LGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_LPUTFIELD_NULLPOINTER
#	define KESO_CHECK_LPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_LPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_SALOAD_NULLPOINTER
#	define KESO_CHECK_SALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_SALOAD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_SASTORE_NULLPOINTER
#	define KESO_CHECK_SASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_SASTORE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_SGETFIELD_NULLPOINTER
#	define KESO_CHECK_SGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_SGETFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_SPUTFIELD_NULLPOINTER
#	define KESO_CHECK_SPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_SPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_ZPUTFIELD_NULLPOINTER
#	define KESO_CHECK_ZPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_ZPUTFIELD_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif

#ifndef KESO_OMIT_CHECK_INVOKEINTERFACE_NULLPOINTER
#	define KESO_CHECK_INVOKEINTERFACE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_INVOKEINTERFACE_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_INVOKESPECIAL_NULLPOINTER
#	define KESO_CHECK_INVOKESPECIAL_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_INVOKESPECIAL_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif


#ifndef KESO_OMIT_CHECK_INVOKEVIRTUAL_NULLPOINTER
#	define KESO_CHECK_INVOKEVIRTUAL_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_) \
		KESO_CHECK_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#else
#	define KESO_CHECK_INVOKEVIRTUAL_NULLPOINTER(_obj_,_method_,_bcpos_, _chkid_)
#endif
#endif
