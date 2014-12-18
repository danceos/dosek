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
 * Contains the OSEK constants representing the different task states.
 *
 * This class used to be the class of Task system objects; to achieve
 * more similarity to the standard Java API, the system object class
 * for task system objects is now {@link java.lang.Thread}.
 */
public final class Task {
	private Task() {  }

	// FIXME These TaskState values are ProOSEK dependant

	/**
	 * ProOSEK constant for the SUSPENDED task state.
	 */
	public static final int SUSPENDED    = 0;

	/**
	 * ProOSEK constant for the READY task state.
	 */
	public static final int READY        = 1;

	/**
	 * ProOSEK constant for the RUNNING task state.
	 */
	public static final int RUNNING      = 2;

	/**
	 * ProOSEK constant for the WAITING task state.
	 */
	public static final int WAITING      = 3;

	/**
	 * Java pendant of the OSEK INVALID_TASK value.
	 */
	public static final Thread INVALID_TASK = null;

	/**
	 * Returns the OSEK implementation specific constant for the SUSPENDED task state.
	 */
	public static int suspendedState() {
		return 0;
	}

	/**
	 * Returns the OSEK implementation specific constant for the READY task state.
	 */
	public static int readyState() {
		return 1;
	}

	/**
	 * Returns the OSEK implementation specific constant for the RUNNING task state.
	 */
	public static int runningState() {
		return 2;
	}

	/**
	 * Returns the OSEK implementation specific constant for the WAITING task state.
	 */
	public static int waitingState() {
		return 3;
	}
}
