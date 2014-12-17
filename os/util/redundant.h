#ifndef __OS_UTIL_REDUNANT_TYPES
#define __OS_UTIL_REDUNANT_TYPES

#include "os/hooks.h"

namespace os { namespace redundant {

template<typename T, template <typename> class Wrapped>
class WithLinkage : public Wrapped<T> {
	T data_store;
 public:
    WithLinkage() : Wrapped<T>(data_store) {}
 };

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

template<typename T = uint32_t>
class MergedDMR {
	 T&  data;
 public:
	 constexpr MergedDMR(T &t) : data(t) {};

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

class EmptyReplicator {
 public:
    void update(void) const {};
    void check(void) const {};
};

template<typename T>
class ClassicTMR  {
	 T&  orig;
     T rep1;
     T rep2;
 public:
	 ClassicTMR(T &t) : orig(t), rep1(t), rep2(t) {};

	 inline void update(void) {
		rep1 = orig;
        rep2 = orig;
	 }

     void check(void) {
        if(!check_and_fix()) {
            CALL_HOOK(FaultDetectedHook, TMRdetected, 0, 0);
        }
     }

 private:
	 inline bool check_and_fix(void) {
        if((orig == rep1) && (orig == rep2)) {
            return true;
        }

        kout << "TMR: Trying to fix" << endl;
        if(orig == rep1) {  // rep2 wrong
            rep2 = orig;    // fix
            return true;
        }

        if(orig == rep2) {  // rep1 wrong
            rep1 = orig;    // fix
            return true;
        }

        if(rep1 == rep2) { // orig wrong
            orig = rep1;
            return true;
        }

        kout << "TMR: oO :( " << endl;
		return false;
	 }
 };




} }

#endif
