#ifndef __INLINE_H__
#define __INLINE_H__

/**
 * @file
 * @ingroup os
 * @brief Inline macros
 */

#define noinline __attribute__ ((noinline))
#define forceinline __inline__ __attribute__((always_inline))

#endif /* __INLINE_H__ */
