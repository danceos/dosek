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
/** (c)

	Copyright (C) 2006-2010 Christian Wawersich, Michael Stilkerich

	This file is part of the KESO Java Runtime Environment.

	KESO is free software: you can redistribute it and/or modify it under the
	terms of the Lesser GNU General Public License as published by the Free
	Software Foundation, either version 3 of the License, or (at your option)
	any later version.

	KESO is distributed in the hope that it will be useful, but WITHOUT ANY
	WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
	FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for
	more details. You should have received a copy of the GNU Lesser General
	Public License along with KESO. If not, see <http://www.gnu.org/licenses/>.

	Please contact keso@cs.fau.de for more info.

	(c)**/

package java.lang;

public final class Runtime {
	private Runtime() { }

	/** Registers a new virtual-machine shutdown hook. */
	public void addShutdownHook(Thread hook) {
		throw new Error("not implemented");
	}

	/** Returns the number of processors available to the Java virtual machine. */
	public int availableProcessors() {
		return 1;
	}

	/** Terminates the currently running Java virtual machine by initiating its shutdown sequence. */
	public void exit(int status) {
		throw new Error("not implemented");
	}

	/** Returns the amount of free memory in the Java Virtual Machine. */
	public long freeMemory() {
		throw new Error("not implemented");
	}

	/** Runs the garbage collector. */
	public void gc() {
		throw new Error("not implemented");
	}

	private static Runtime _rt;
	/** Returns the runtime object associated with the current Java application. */
	public static Runtime getRuntime() {
		if(_rt == null)
			_rt = new Runtime();
		return _rt;
	}

	/** Forcibly terminates the currently running Java virtual machine. */
	public void halt(int status) {
		throw new Error("not implemented");
	}

	/** Returns the maximum amount of memory that the Java virtual machine will attempt to use. */
	public long maxMemory() {
		return totalMemory();
	}

	/** De-registers a previously-registered virtual-machine shutdown hook. */
	public boolean removeShutdownHook(Thread hook) {
		throw new Error("not implemented");
	}

	/** Returns the total amount of memory in the Java virtual machine. */
	public long totalMemory() {
		return 0L;
	}
}

