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
 * This memory type allows to an unsigned 8-bit value.
 */
final public class MT_U8 extends MT {

	private MT_U8 self;

	private MT_U8() {  }

	/**
	 * Reads the value from the target location of the mapping.
	 *
	 * @return the read value
	 */
	public int get() { return self.get(); }

	/**
	 * Stores a value to the target location of the mapping.
	 *
	 * @param i  the value to store.
	 */
	public void set(int i) { self.set(i); }

	/**
	 * Computes the bitwise AND of the mapped value and the given mask,
	 * and overwrites the mapped value with the result of this computation.
	 *
	 * @param i  the mask used in the operation
	 */
	public void and(int i) { self.and(i); }

	/**
	 * Computes the bitwise OR of the mapped value and the given mask,
	 * and overwrites the mapped value with the result of this computation.
	 *
	 * @param i  the mask used in the operation
	 */
	public void or(int i) { self.or(i); }

	/**
	 * Computes the bitwise exclusive OR (XOR) of the mapped value and the given
	 * mask, and overwrites the mapped value with the result of this computation.
	 *
	 * @param i  the mask used in the operation
	 */
	public void xor(int i) { self.xor(i); }

	/**
	 * Sets the given bit in the mapped value.
	 *
	 * @param i position of the bit to be set (0-7)
	 */
	public void setBit(int i) { self.setBit(i); }

	/**
	 * Clears the given bit in the mapped value.
	 *
	 * @param i position of the bit to be cleared (0-7)
	 */
	public void clearBit(int i) { self.clearBit(i); }

	/**
	 * Checks if a given bit of the mapped value is set
	 *
	 * @param i position of the bit to be checked (0-7)
	 * @return true if the bit is set, false otherwise
	 */
	public boolean isBitSet(int i) { return self.isBitSet(i); }

	/**
	 * Checks if a given bit of the mapped value is cleared
	 *
	 * @param i position of the bit to be checked (0-7)
	 * @return true if the bit is cleared, false otherwise
	 */
	public boolean isBitClear(int i) { return self.isBitClear(i); }

	/**
	 * Returns true if both mapped fields are mapped to the same address.
	 */
	public boolean equals(Object o) { return (self.hashCode()==((MT_U8)o).hashCode()); }

	/** {@inheritDoc} */
	public int hashCode() { return self.hashCode(); }

	public String toString() { return "U8: "+self.get(); }
}
