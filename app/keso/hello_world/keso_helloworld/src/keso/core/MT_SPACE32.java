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
 * This memory type allows to define a 32-bit gap in a memory-mapped
 * class definition.
 *
 * The memory location that this field maps to will not be accessible
 * in any way.
 */
final public class MT_SPACE32 extends MT {

	private MT_SPACE32 self;

	private MT_SPACE32() { }

	/**
	 * Returns true if both mapped fields are mapped to the same address.
	 */
	public boolean equals(Object o) { return (self.hashCode()==((MT_SPACE32)o).hashCode()); }

	/** {@inheritDoc} */
	public int hashCode() { return self.hashCode(); }

	public String toString() { return "SPACE32"; }
}
