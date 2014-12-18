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
 * This memory type allows to define a mapped C++ bool value.
 *
 * This type is useful to access data structures shared with C++
 * code. The actual size occupied by the structure depends on the
 * data size of the C++ data type bool on the respective target
 * platform. It is normally not useful for device memory.
 *
 */
final public class MT_BOOLEAN extends MT {

	private MT_BOOLEAN self;

	private MT_BOOLEAN() { }

	/**
	 * Reads the value from the target location of the mapping.
	 *
	 * @return the read value
	 */
	public boolean get() { return self.get(); }

	/**
	 * Stores a value to the target location of the mapping.
	 *
	 * @param b  the value to store.
	 */
	public void set(boolean b) { self.set(b); }

	/**
	 * Returns true if both mapped fields are mapped to the same address.
	 */
	public boolean equals(Object o) { return (self.hashCode()==((MT_BOOLEAN)o).hashCode()); }

	/** {@inheritDoc} */
	public int hashCode() { return self.hashCode(); }

	/**
	 * Returns "true" if the value is true and returns "false" if the value is false.
	 */
	public String toString() { return Boolean.toString(self.get()); }
}
