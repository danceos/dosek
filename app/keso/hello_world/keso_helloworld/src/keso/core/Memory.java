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
 * Memory objects provide a low level, untyped interface to access memory areas
 * outside the managed memory regions. The concept is basically that same as
 * RawMemoryAccess as defined in the Real-time Specification for Java (RTSJ),
 * KESO's implementation is currently not API compatible though.
 *
 * A Memory object internally refers to a memory region that is defined by a
 * start address and a size. Memory objects can only be created using the
 * special methods of the {@link MemoryService}, but may also be
 * returned by other internal services such as the messageport or shared
 * memory APIs of the CiAO backend.
 */
public final class Memory {
	/**
	 * Memory objects may only be created by the MemoryService.
	 */
	private Memory() {}

	/**
	 * Provides the size of the memory area referenced by the Memory object.
	 *
	 * @return size of the referenced memory area
	 */
	public int getSize() {
		return -1;
	}

	/**
	 * Creates a new Memory object that references a subarea of the current Memory object.
	 * It may be used if only a part of an Memory block shall be accessible by
	 * another method or class.
	 *
	 * @param offset The offset of the new start address relative to the old start address ( 0<= offset <= getSize() )
	 * @param length The size subarea. ( 0 < length <= (getSize() - offset) )
	 *
	 * @return A new Memory object referencing the defined subarea, or null if for illegal parameter ranges.
	 */
	public Memory getPart(int offset, int length) {
		return null;
	}

	/**
	 * Read a byte at the specified offset from the beginning of
	 * the represented memory block.
	 *
	 * @param  offset the offset into the memory block to read from
	 * @return the read byte
	 */
	public byte get8(int offset) { return 0; }

	/**
	 * Write a byte at the specified offset from the beginning of
	 * the represented memory block.
	 *
	 * @param offset the offset into the memory block to write to
	 * @param value  the value that will be written
	 */
	public void set8(int offset, byte value) { }

	/**
	 * Read a 16-bit value at the specified offset from the beginning of
	 * the represented memory block.
	 *
	 * @param offset the offset into the memory block to read from
	 * @return the read value
	 */
	public short get16(int offset) { return 0; }

	/**
	 * Write a 16-bit value at the specified offset from the beginning of
	 * the represented memory block.
	 *
	 * @param offset the offset into the memory block to write to
	 * @param value the value that will be written
	 */
	public void set16(int offset, short value) { }

	/**
	 * Read a 32-bit value at the specified offset from the beginning of
	 * the represented memory block.
	 *
	 * @param  offset the offset into the memory block to read from
	 * @return the read value
	 */
	public int get32(int offset) { return 0; }

	/**
	 * Write a 32-bit value at the specified offset from the beginning of
	 * the represented memory block.
	 *
	 * @param offset the offset into the memory block to write to
	 * @param value  the value that will be written
	 */
	public void set32(int offset, int value) {  }

	/**
	 * Read a 32-bit floating point value at the specified offset from the
	 * beginning of the represented memory block.
	 *
	 * @param  offset the offset into the memory block to read from
	 * @return the read value
	 */
	public float getFloat(int offset) { return 0.0f; }

	/**
	 * Write a 32-bit floating point value at the specified offset from the
	 * beginning of the represented memory block.
	 *
	 * @param offset the offset into the memory block to write to
	 * @param value  the value that will be written
	 */
	public void setFloat(int offset, float value) { }

	/**
	 * Performs the logical AND on a byte value in the area using the given
	 * mask and overwrites the original value with the result.
	 *
	 * @param offset offset of the value within the referenced memory area
	 * @param mask   mask to be used in the operation
	 */
	public void and8(int offset, int mask) { }

	/**
	 * Performs the logical AND on a 16-bit value in the area using the given
	 * mask and overwrites the original value with the result.
	 *
	 * @param offset offset of the value within the referenced memory area
	 * @param mask   mask to be used in the operation
	 */
	public void and16(int offset, int mask) { }

	/**
	 * Performs the logical AND on a 32-bit value in the area using the given
	 * mask and overwrites the original value with the result.
	 *
	 * @param offset offset of the value within the referenced memory area
	 * @param mask   mask to be used in the operation
	 */
	public void and32(int offset, int mask) { }

	/**
	 * Performs the logical OR on a byte value in the area using the given
	 * mask and overwrites the original value with the result.
	 *
	 * @param offset offset of the value within the referenced memory area
	 * @param mask   mask to be used in the operation
	 */
	public void or8(int offset, int mask) { }

	/**
	 * Performs the logical OR on a 16-bit value in the area using the given
	 * mask and overwrites the original value with the result.
	 *
	 * @param offset offset of the value within the referenced memory area
	 * @param mask   mask to be used in the operation
	 */
	public void or16(int offset, int mask) { }

	/**
	 * Performs the logical OR on a 32-bit value in the area using the given
	 * mask and overwrites the original value with the result.
	 *
	 * @param offset offset of the value within the referenced memory area
	 * @param mask   mask to be used in the operation
	 */
	public void or32(int offset, int mask) { }

	/**
	 * Performs the logical exclusive OR (XOR) on a byte value in the area using
	 * the given mask and overwrites the original value with the result.
	 *
	 * @param offset offset of the value within the referenced memory area
	 * @param mask   mask to be used in the operation
	 */
	public void xor8(int offset, int mask) { }

	/**
	 * Performs the logical exclusive OR (XOR) on a 16-bit value in the area using
	 * the given mask and overwrites the original value with the result.
	 *
	 * @param offset offset of the value within the referenced memory area
	 * @param mask   mask to be used in the operation
	 */
	public void xor16(int offset, int mask) { }

	/**
	 * Performs the logical exclusive OR (XOR) on a 32-bit value in the area using
	 * the given mask and overwrites the original value with the result.
	 *
	 * @param offset offset of the value within the referenced memory area
	 * @param mask   mask to be used in the operation
	 */
	public void xor32(int offset, int mask) { }
}
