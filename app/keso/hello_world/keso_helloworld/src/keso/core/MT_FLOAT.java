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
 * This memory type allows to define a mapped single precision float value (32 bits).
 */
final public class MT_FLOAT extends MT {

	private MT_FLOAT self;

	private MT_FLOAT() {  }

	/**
	 * Reads the value from the target location of the mapping.
	 *
	 * @return the read value
	 */
	public float get() { return self.get(); }

	/**
	 * Stores a value to the target location of the mapping.
	 *
	 * @param i  the value to store.
	 */
	public void set(float i) { self.set(i); }

	/**
	 * Returns true if both mapped fields are mapped to the same address.
	 */
	public boolean equals(Object o) { return (self.hashCode()==((MT_FLOAT)o).hashCode()); }

	/** {@inheritDoc} */
	public int hashCode() { return self.hashCode(); }

	/**
	 * Returns "true" if the value is true and returns "false" if the value is false.
	 */
	public String toString() { return "FLOAT: "+self.get(); }
}
