// @formatter:off
/**(c)

  Copyright (C) 2006-2013 Christian Wawersich, Michael Stilkerich,
                          Christoph Erhardt

  This file is part of the KESO Java Runtime Environment.

  KESO is free software: you can redistribute it and/or modify it under the
  terms of the Lesser GNU General Public License as published by the Free
  Software Foundation, either version 3 of the License, or (at your option)
  any later version.

  KESO is distributed in the hope that it will be useful, but WITHOUT ANY
  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
  FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
  more details. You should have received a copy of the GNU Lesser General
  Public License along with KESO. If not, see <http://www.gnu.org/licenses/>.

  Please contact keso@cs.fau.de for more info.

  (c)**/
// @formatter:on

package keso.core;

/**
 * The MemoryService provides services to access physical raw memory areas at
 * specific addresses, allocation of new raw memory areas for use in shared
 * memory, and methods to create {@link MemoryMappedObject}s.
 */
public final class MemoryService {
	/**
	 * Provides access to a raw device memory area using a statically allocated
	 * {@link Memory} object.
	 *
	 * Device Memory can be used to access physical memory at a specified address.
	 * This is necessary e.g. to access memory mapped device registers.
	 * This function allocates an immortal {@link Memory} object to access device memory.
	 * This object is unique to that call site. Subsequent invocations at the same
	 * call site will always return the SAME object refering to the memory area as
	 * defined by the last invocation. If this it not what you want, you may want
	 * to consider {@link #allocDynamicDeviceMemory(int,int)}.
	 *
	 * @param  start start address of the memory area.
	 * @param  size  size in bytes of the memory area.
	 * @return A {@link Memory} object for accessing the specified memory area.
	 */
	public static Memory allocStaticDeviceMemory(int start, int size) { return null; }

	/**
	 * Provides access to a raw device memory area using a dynamically allocated
	 * {@link Memory} object.
	 * Device Memory can be used to access physical memory at a specified address.
	 * This is necessary e.g. to access memory mapped device registers.
	 * This function allocates a {@link Memory} object on the domain's heap at runtime that
	 * references the memory area defined by the given parameters.
	 *
	 * HINT:
	 * Prefer the use of {@link #allocStaticDeviceMemory} or
	 * {@link #mapStaticDeviceMemory} to create a smaller application.
	 *
	 * @param  start start address of the memory area.
	 * @param  size  size in bytes of the memory area.
	 * @return A {@link Memory} object for accessing the specified memory area.
	 */
	public static Memory allocDynamicDeviceMemory(int start, int size) { return null; }

	/**
	 * Establishes a new mapping of a memory mapped class to a given address using a
	 * statically allocated {@link MemoryMappedObject}.
	 *
	 * Device Memory can be used to access physical memory at a specified address.
	 * This is necessary e.g. to access memory mapped device registers.
	 *
	 * This function allocates an immortal {@link MemoryMappedObject} object to
	 * access device memory.  For the program this means, that subsequent calls
	 * of the functions at one particular call site will always return the same
	 * object.
	 *
	 * Both the name of the mapped class and the target address not to be constants.
	 *
	 * @param  start start address of the memory area.
	 * @param  type  the (qualified) class name of type (needs to be a String constant!).
	 * @return A {@link MemoryMappedObject} for accessing the specified memory area.
	 */
	public static MemoryMappedObject mapStaticDeviceMemory(int start, String type) { return null; }

	/**
	 * Establishes a new mapping of a memory mapped class to a given address using a
	 * heap-allocated {@link MemoryMappedObject}.
	 *
	 * Device memory can be used to access physical memory at a specified address.
	 * This is necessary e.g. to access memory mapped device registers.
	 *
	 * This function dynamically allocates a {@link MemoryMappedObject} to access device memory.
	 *
	 * Both the name of the mapped class and the target address need to be constants.
	 *
	 * @param  start start address of the memory area.
	 * @param  type  the (qualified) class name of type (needs to be a String constant!).
	 * @return A {@link MemoryMappedObject} for accessing the specified memory area.
	 */
	public static MemoryMappedObject mapDeviceMemory(int start, String type) { return null; }

	/**
	 * This function allocates a memory block that can be used like physical
	 * memory. In contrast to device memory, a memory area of the specified size
	 * will be allocated, but not on the domain heap. This memory area can be
	 * used as shared memory.
	 *
	 * The function has a maximum complexity O(n) to find a free block and to
	 * defragment the shared memory area, where n depends on the fragmentation
	 * of the memory. Therefore do not allocate shared memory in a time
	 * critical execution path.
	 *
	 * HINT:
	 * Prefer the use of {@link #allocStaticMemory} or
	 * {@link #allocStaticMemoryHandle} to create a smaller application without
	 * the need of a dynamic memory managment.
	 *
	 * @param size  size of the requested memory area
	 * @return a {@link Memory} object for accessing the allocated memory area
	 */
	public static Memory allocMemory(int size) { return null; }

	/**
	 * This function will allocate an immortal memory block that can be used like
	 * physical memory and an immortal {@link Memory} object to access the area. In
	 * contrast to device memory it is not possible to define a start address.
	 * The memory area of the specified size will be allocated outside the
	 * domain heap.
	 *
	 * This function allocates an immortal {@link Memory} object and an immortal memory area.
	 *
	 * @param  size size of the requested memory area (compile time constant!)
	 * @return a {@link Memory} object for accessing the allocated memory area
	 */
	public static Memory allocStaticMemory(int size) { return null; }

	/**
	 * This function allocates a static and immortal {@link MemoryMappedObject}. For
	 * the program this means, that subsequent calls will always return the
	 * same object.
	 *
	 * @param  mem     {@link Memory} object representing the memory area.
	 * @param  offset  the offset inside the memory area.
	 * @param  type    the class name of type.
	 * @return A {@link MemoryMappedObject} for accessing the specified memory area. null if mem was null.
	 */
	public static MemoryMappedObject mapMemoryToStaticObject(Memory mem, int offset, String type) { return null; }

	/**
	 * Allocates a new object of the given type from the heap and establishes a
	 * mapping to a subregion of the given {@link Memory} area.
	 *
	 * @param  mem     {@link Memory} object representing the memory area.
	 * @param  offset  the offset inside the memory area.
	 * @param  type    the class name of type.
	 * @return A {@link MemoryMappedObject} for accessing the specified memory area. null if mem was null.
	 */
	public static MemoryMappedObject mapMemoryToObject(Memory mem, int offset, String type) { return null; }

	/**
	 * This function creates a {@link Memory} object for an empty memory range.
	 *
	 * This function allocates an immortal and empty {@link Memory} object as
	 * handle for later memory access. It is the same as {@link #allocStaticMemory(int)}(0).
	 * The Handle can be used together with {@link #adjustMemory(Memory,int,Memory,int)}
	 * to access memory ranges.
	 */
	public static Memory allocStaticMemoryHandle() { return null; }

	/**
	 * This function changes the memory address and range of a {@link Memory} object to
	 * a subarea of another {@link Memory} object.
	 *
	 * @param dst  the {@link Memory} object which is adjusted.
	 * @param src  the {@link Memory} object which provides access to the source memory.
	 * @param soff the offset inside the source memory.
	 * @param len  the length of the memory range.
	 */
	public static void adjustMemory(Memory src, int soff, Memory dst, int len) { }

	/**
	 * Release the memory range.
	 *
	 * This effectively revokes the access to the memory area referenced by the
	 * {@link Memory} object. Further access operations on the {@link Memory} object will fail,
	 * unless the {@link Memory} object has been readjusted
	 * ({@link #adjustMemory(Memory,int,Memory,int)}).
	 */
	public static void releaseMemory(Memory mem) { }

	/**
	 * Copy data from one raw memory area to another one.
	 *
	 * HINT:
	 * Use memory ranges ({@link MemoryService#adjustMemory(Memory,int,Memory,int)}) if possible.
	 *
	 * @param src  source {@link Memory} object
	 * @param soff offset in source area
	 * @param dst  destination {@link Memory} object
	 * @param doff offset in destination area
	 * @param len  number of bytes to copy
	 */
	public static void copy(Memory src, int soff, Memory dst, int doff, int len) { }
}
