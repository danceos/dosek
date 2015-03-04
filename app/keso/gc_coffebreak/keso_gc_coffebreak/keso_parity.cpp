/*
 * NOTE: This file is generated. Any edits will be overwritten.
 * Instead of editing this file, edit the template files mentioned below.
 */

/**********************************************************************
 * Generated from c-templates/CodeTemplate/parity/parity_chk_common.c *
 **********************************************************************/
#include "keso_parity.h"
#include "global.h"

#ifndef KESO_OMIT_SAFECHECKS
	#ifndef KESO_PRODUCTION
		void keso_throw_parity(const char *reason, const char *method, int bcpos, const void *obj) {
			KESO_PRINTF("parity check exception at %s (in %s, BCP %d, ADDRESS 0x%x)\n", reason, method, bcpos, obj);
			/*keso_throw_error();*/
			ShutdownOS(E_NOT_OK);
		}
	#else /* defined(KESO_PRODUCTION) */
		#ifdef KESO_USE_CODED_REFS_INLINE
			/* TODO keso_throw_error does not seem to be declared, when
			 * parity_chk.c's Header is included */
			void keso_throw_parity_error() {
				keso_throw_error();
			}
		#endif /* defined(KESO_USE_CODED_REFS_INLINE) */
	#endif /* defined(KESO_PRODUCTION) */
#endif /* defined(KESO_OMIT_SAFECHECKS) */
#if defined(KESO_USE_CODED_REFS_ON_GET_SET) || defined(KESO_USE_CODED_REFS) || defined(KESO_USE_CODED_REFS_DOM) || defined(KESO_CODED_REF_CXXP_PARITY)
	#ifdef KESO_COUNT_CHECKS
		int cnt_h = 0;
		int cnt_ah = 0;
		int cnt_r = 0;
	#endif
#endif
/********************************************************************
 * Generated from c-templates/CodeTemplate/parity/parity_chk_pint.c *
 ********************************************************************/

#ifdef KESO_PARITY_CHK_NEEDS_PINT

 void *keso_check_parity_pint(void *_obj KESO_PARITY_CHK_PINT_EXCEPTION_PARAMS) {
	KESO_COUNT_CHECK(_chkid_);
	if (unlikely(KESO_GET_PARITY(((uintptr_t)_obj)) != 0)) {
		keso_throw_parity("reference",
#ifdef KESO_PRODUCTION
		"<unknown method>", -1,
#else
		_method_, _bcpos_,
#endif
		 _obj);
	}
	return _obj;
}

 uintptr_t keso_add_parity_pint(void *_obj) {
	unsigned char parity_bit = 0;
	parity_bit = KESO_GET_PARITY((unsigned int) (_obj));
	return (unsigned int) (_obj) | (parity_bit << 1);
}

 void keso_set_parity_pint(void **pobj) {
	*pobj = (void*) keso_add_parity_pint(*pobj);
}

 uintptr_t keso_check_and_decode_pint(void *_obj_ KESO_PARITY_CHK_PINT_EXCEPTION_PARAMS) {
	keso_check_parity_pint(_obj_ KESO_PARITY_CHK_PINT_EXCEPTION_ARGS);
	return KESO_DECODE_PINT(_obj_);
}

#endif

/******************************************************************
 * Generated from c-templates/CodeTemplate/parity/parity_chk_hc.c *
 ******************************************************************/


#ifdef KESO_MAGIC_VALUE_OR_HEADER_CHECK
	/* Make sure obj is non-null and decoded */
	 class_id_t keso_decode_header(const object_t *obj, const char *_method_) {
		class_id_t class_id;
		class_id = obj->class_id;

#ifdef KESO_MAGIC_VALUE_HEADER
		//mask: 1 byte long. false on bits where parity is stored, otherwise true
		char mask = 0;
#ifdef KESO_USE_CODED_REFS_HEADER_CHECK
		mask = 1 << KESO_CLASS_ID_PARITY_BIT_SHIFT;
#endif
#ifdef KESO_USE_CODED_REFS_CHECK_ARRAYLENGTH
		mask &= 1 << KESO_ARRAYLENGTH_PARITY_BIT_SHIFT;
#endif
		mask ^= 0xff;
		
		// check magic value in object header. throw exception if not correct
		if ((obj->bitfld & mask) != KESO_OBJECT_HEADER_MAGIC_VALUE){
			keso_throw_parity("header_magic_value", _method_, -1, obj);
		}
#endif //KESO_MAGIC_VALUE_HEADER

#ifdef KESO_USE_CODED_REFS_HEADER_CHECK
		#ifdef KESO_COUNT_CHECKS
			cnt_h++;
		#endif

		const unsigned int CLASS_ID_BITS = sizeof(class_id_t)*8;
		unsigned int bits, parity;
		bits = class_id | ((obj->bitfld & KESO_CLASS_ID_PARITY_BIT) << CLASS_ID_BITS);
		if (CLASS_ID_BITS == 8) {
			parity = KESO_GET_PARITY16(bits);
		} else {
			parity = KESO_GET_PARITY32(bits);
		}
		if (unlikely(parity != 0)) {
			keso_throw_parity("decode_header", _method_, -1, obj);
		}
#endif //KESO_USE_CODED_REFS_HEADER_CHECK

		return class_id;
	}
#endif //KESO_MAGIC_VALUE_OR_HEADER_CHECK


#ifdef KESO_MAGIC_VALUE_OR_HEADER_CHECK
	/* Make sure obj is non-null and decoded */
	 void keso_init_parity_header(object_t *obj) {

#ifdef KESO_USE_CODED_REFS_HEADER_CHECK
		unsigned int parity = KESO_GET_PARITY16(obj->class_id); /* TODO evtl nur 8... */
		obj->bitfld |= parity << KESO_CLASS_ID_PARITY_BIT_SHIFT;
#endif //KESO_USE_CODED_REFS_HEADER_CHECK

#ifdef KESO_MAGIC_VALUE_HEADER
		// init with magic value
		obj->bitfld |= KESO_OBJECT_HEADER_MAGIC_VALUE;
#endif //KESO_MAGIC_VALUE_HEADER

	}
#endif //KESO_MAGIC_VALUE_OR_HEADER_CHECK

#ifdef KESO_USE_CODED_REFS_CHECK_ARRAYLENGTH
	 array_size_t keso_check_and_decode_arraylength(const array_t *obj, const char *_method_, int _bcpos_, int _chkid_) {
		#ifdef KESO_COUNT_CHECKS
			cnt_ah++;
		#endif
		const unsigned int ARRAYLENGTH_BITS = sizeof(array_size_t) * 8;
		array_size_t size;
		unsigned int bits, parity, parity_bit;
		size = obj->size;
		parity_bit = (obj->bitfld >> KESO_ARRAYLENGTH_PARITY_BIT_SHIFT) & 1;
		/* put parity-bit in sign-bit <- assume size is never > JINT_MAX */
		bits = size | (parity_bit << (ARRAYLENGTH_BITS-1));
		if (ARRAYLENGTH_BITS == 8) {
			parity = KESO_GET_PARITY8(bits);
		} else if (ARRAYLENGTH_BITS == 16) {
			parity = KESO_GET_PARITY16(bits);
		} else {
			parity = KESO_GET_PARITY32(bits);
		}
		if (unlikely(parity != 0)) {
			keso_throw_parity("arraylength", _method_, _bcpos_, (const object_t *) obj);
			return 0;
		}
		return size;
	}

	/* Make sure obj is non-null and decoded */
	 object_t *keso_add_parity_arraylength(array_t *obj) {
		unsigned int parity = KESO_GET_PARITY32(obj->size); /* TODO evtl nur 8 oder 16 */
		obj->bitfld |= parity << KESO_ARRAYLENGTH_PARITY_BIT_SHIFT;
		return (object_t *) obj;
	}
#endif

/********************************************************************
 * Generated from c-templates/CodeTemplate/parity/parity_chk_refs.c *
 ********************************************************************/
/*******************************************************************
 * Generated from c-templates/CodeTemplate/parity/parity_chk_dom.c *
 *******************************************************************/
/********************************************************************
 * Generated from c-templates/CodeTemplate/parity/parity_chk_dref.c *
 ********************************************************************/
