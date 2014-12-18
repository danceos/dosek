#ifndef __keso_compiler_extensions_h__
#define __keso_compiler_extensions_h__

#define likely(x)   __builtin_expect((x),1)
#define unlikely(x)   __builtin_expect((x),0)
#define NORETURN      __attribute__ ((noreturn))
#define ALIGN4        __attribute__ ((aligned (4)))
#define KESO_ALIGN(x) __attribute__ ((aligned (x)))
#define ATTR_CONST    __attribute__ ((const))
#define ATTR_PURE     __attribute__ ((pure))
#define ATTR_MAYALIAS __attribute__ ((may_alias))
#define KESO_INLINE   __inline__
#define KESO_CONST    __const__
#define KESO_NOINLINE __attribute__((noinline))
#define KESO_COMPILER_MEMORY_BARRIER_AT(addr) asm volatile ("" :"=m" (addr) :"m" (addr))
#define KESO_ENSURE_MEMORY_WRITES_AT(addr) asm volatile ("" : :"m" (addr))
#ifdef __cplusplus
	#define KESO_EXTERN_C extern "C"
	#define KESO_EXTERN_C_BEGIN extern "C" {
	#define KESO_EXTERN_C_END }
#else
	#define KESO_EXTERN_C
	#define KESO_EXTERN_C_BEGIN
	#define KESO_EXTERN_C_END
#endif
#define KESO_STATIC_ASSERT_BASE0(COND,MSG) typedef char keso_static_assertion_##MSG[(!!(COND))*2-1]
#define KESO_STATIC_ASSERT_BASE1(X,L,MSG) KESO_STATIC_ASSERT_BASE0(X,at_line_##L##_##MSG)
#define KESO_STATIC_ASSERT_BASE2(X,L,MSG) KESO_STATIC_ASSERT_BASE1(X,L,MSG)
#define KESO_STATIC_ASSERT(COND,MSG) KESO_STATIC_ASSERT_BASE2(COND,__LINE__,MSG)
#endif
