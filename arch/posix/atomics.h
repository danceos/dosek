#ifndef _UTIL_ATOMICS_H
#define _UTIL_ATOMICS_H

namespace arch {
	template<typename P, typename V>
	static bool compare_and_swap(P *ptr, V oldval, V newval) {
		return __sync_bool_compare_and_swap(ptr, oldval, newval);
	}

	template<typename P, typename V>
	static V atomic_fetch_and_add(P *ptr, V value) {
		return __sync_fetch_and_add(ptr, value);
	}

	template<typename P, typename V>
	static V atomic_fetch_and_sub(P *ptr, V value) {
		return __sync_fetch_and_sub(ptr, value);
	}

	static void atomic_memory_barrier() {
		__atomic_thread_fence(__ATOMIC_SEQ_CST);
	}
}

#endif
