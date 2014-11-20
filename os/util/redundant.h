#ifndef __OS_UTIL_REDUNANT_TYPES
#define __OS_UTIL_REDUNANT_TYPES

#include "os/hooks.h"

namespace os { namespace redundant {

/**
 * "Redundant" data type without redudancy
 */
template<typename T>
class Plain {
	T  & data;
public:

	constexpr Plain(T &t) : data(t) {};

	inline void set(T x) const {
		data = x;
	}

	inline T get() const {
		return data;
	}

	inline bool check() const {
		return true;
	}
};

/**
 * Redunant data type that stores a parity bit in (1<<31) bitposition
 */
template<typename T>
class HighParity {
	T&  data;
public:

	constexpr HighParity(T &t) : data(t) {};

	inline void set(T x) const {
		intptr_t _data	= (intptr_t) x;
		if(__builtin_parity(_data) == 1) {
			data = (T) _data;
		} else {
			data = (T) (_data | 0x80000000);
		}
	}

	inline T get() const {
		return (T) ((uint32_t)data & 0x7FFFFFFF);
	}

	inline bool check() const {
		if (__builtin_parity((uint32_t) data) != 1) {
			CALL_HOOK(FaultDetectedHook, PARITYdetected, (uint32_t)data, 0);
			return false;
		}
		return true;
	}
};

class MergedDMR {
	 uint32_t&  data;
 public:
	 constexpr MergedDMR(uint32_t &t) : data(t) {};

	 inline void set(uint16_t x) const {
		 data = (x) | (x << 16);
	 }

	 inline uint16_t get() const {
		 return data & 0xffff;
	 }

	 inline bool check() const {
		 if ((data & 0xffff) != (data >> 16)) {
			 CALL_HOOK(FaultDetectedHook, DMRdetected,
					   data & 0xffff,
					   data >> 16);
			 return false;
		 }
		 return true;
	 }
 };


} }

#endif
