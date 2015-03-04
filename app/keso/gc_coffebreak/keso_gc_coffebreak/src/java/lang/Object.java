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

public class Object {
	public Class getClass() {
		throw new Error("not implemented");
	}

	public int hashCode() {
		throw new Error("This method must be implemented by the runtime system.");
	}

	public boolean equals(Object obj) {
		return false;
	}

	public void notifyAll() {
		throw new Error("This method must be implemented by the runtime system.");
	}

	public void wait() {
		throw new Error("This method must be implemented by the runtime system.");
	}

	public void wait(long timeout) {
		throw new Error("This method must be implemented by the runtime system.");
	}

	public void notify() {
		throw new Error("This method must be implemented by the runtime system.");
	}

	public String toString() {
		return new String("objref:" + hashCode());
	}

	protected void finalize() throws Throwable { }

	protected Object clone() throws CloneNotSupportedException {
		throw new Error("This method must be implemented by the runtime system.");
	}
}
