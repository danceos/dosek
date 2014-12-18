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

import java.lang.Thread;

public final class EventService {

	/**
	 * Sets one or more events specified in <event> for the extended task
	 * specified by <taskID>.
	 *
	 * May be called from any task and ISR cat.2
	 */
	public static int setEvent(Thread taskID, int evMask) { return 0; }

	/**
	 * Events of the calling extended task are cleared according to <event>.
	 */
	public static int clearEvent(int evMask) { return 0; }

	/**
	 * Query the events of a task specified by <taskID>.
	 * The result is returned as eventMask.
	 *
	 * May be called from any task and ISR cat.2
	 *
	 * TODO this does not return the statustype. Throw an OSEKException
	 * in case of an error. We should do this generally for all our syscalls
	 * and make an OSEKException class that has the StatusType encapsulated.
	 */
	public static int getEvent(Thread taskID) { return 0; }

	/**
	 * Wait until at least one of the events specified by <event> are set
	 * for the calling extended Task.
	 */
	public static int waitEvent(int evMask) { return 0; }
}
