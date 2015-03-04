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
 * This class contains ProOSEK services (these are not defined in the OSEK spec)
 * to deal with counters.
 *
 * The services of this class are especially useful to advance user managed
 * counters that do not have a hardware timer attached.
 */

public final class CounterService {
	/**
	 * Advance <counter> by one from task level.
	 */
	public static int advanceCounter(int counterID) { return 0; }

	/**
	 * Advance <counter> by one from an ISR.
	 *
	 * The user must ensure that calls to iAdvanceCounter do not overlap.
	 */
	public static int iAdvanceCounter(int counterID) { return 0; }
}
