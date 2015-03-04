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
 * This memory type allows to read-only map an unsigned 32-bit value.
 */
final public class MT_U32RO extends MT {

	private MT_U32RO self;

	private MT_U32RO() { }

	/**
	 * Reads the value from the target location of the mapping.
	 *
	 * @return the read value
	 */
	public int get() { return self.get(); }

	/**
	 * Checks if a given bit of the mapped value is set
	 *
	 * @param i position of the bit to be checked (0-31)
	 * @return true if the bit is set, false otherwise
	 */
	public boolean isBitSet(int i) { return self.isBitSet(i); }

	/**
	 * Checks if a given bit of the mapped value is cleared
	 *
	 * @param i position of the bit to be checked (0-31)
	 * @return true if the bit is cleared, false otherwise
	 */
	public boolean isBitClear(int i) { return self.isBitClear(i); }

	/**
	 * Returns true if both mapped fields are mapped to the same address.
	 */
	public boolean equals(Object o) { return (self.hashCode()==((MT_U32RO)o).hashCode()); }

	/** {@inheritDoc} */
	public int hashCode() { return self.hashCode(); }

	public String toString() { return "U32RO: "+self.get(); }
}
