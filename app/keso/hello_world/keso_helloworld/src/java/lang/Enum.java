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

package java.lang;

public class Enum<E extends Enum<E>> {

	final private int ordinal;
	final private String name;

	protected Enum(String name, int ordinal) {
		this.name = name;
		this.ordinal = ordinal;
	}

	public final String name() {
		return name;
	}

	public final int ordinal() {
		return ordinal;
	}

	public final int compareTo(E obj) {
		Enum e = (Enum)obj;
		return e.ordinal - this.ordinal;
	}

	public final boolean equals(Object obj) {
		return this==obj;
	}

	public final int hashCode() {
		return ordinal;
	}

	public String toString() {
		return name;
	}

	protected final Object clone() {
		throw new Error("CloneNotSupprtedException");
	}

	public static <T extends Enum<T>> T valueOf(Class<T> enumType, String name) {
		return Enum.valueOf(enumType, name);
	}
}
