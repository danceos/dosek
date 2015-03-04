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

public final class OSService {
	/**
	 * Returns the current application mode. May be used to write mode dependant
	 * code.
	 */
	public static int getActiveApplicationMode() { return 0; }

	/**
	 * The user may use this call to start the OS in a specific application mode.
	 *
	 * May only be called from outside the OS.
	 */
	public static void startOS(int appMode) {}

	/**
	 * This service may be called to abort the whole system (emergency off).
	 *
	 * If a ShutdownHook is specified, it is always called with <error> as
	 * parameter before the system is shut off.
	 */
	public static void shutdownOS(int error) {}
}
