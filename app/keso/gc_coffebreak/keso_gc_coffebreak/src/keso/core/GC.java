package keso.core;

public class GC {

	/**
	 * Return the current heap size.
	 */
	static public int getHeapSize() {
		/* KNI */ 
		return 0;
	}

	/**
	 * GC barrier.
	 */
	static public void barrier() {
		/* KNI */ 
	}

	/**
	 * Garbage collector guards can be used to ensure that enought
	 * memory is avialabel for object allocation.
	 *
	 * GCTMode="UseMemoryGuards"
	 *
	 * EXPERIMENTAL
	 */
	static public void guard(int ensure, int count) {
		/* KNI */ 
	}
}
