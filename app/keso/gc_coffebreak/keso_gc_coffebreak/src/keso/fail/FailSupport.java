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

package keso.fail;

/**
 * Produce nice (non mangled) failmarkers (fail_start_trace and
 * fail_stop_trace) by using a weavelet.
 *
 * Please do none use each of the defined functions just once!
 * (otherwise fail might get a bit disturbed, or it might even fail completely)
 */
public final class FailSupport {
	/** Call the fail_start_trace symbol here
	 */
	public static void startTrace() { }

	/** Call the fail_stop_trace symbol here
	 */
	public static void stopTrace() { }

	/** Call the fail_undetected_failure_marker symbol here
	 */
	public static void markUndetectedFailure() {}

	/** Call the fail_ok_marker here
	 */
	public static void markSuccess() {}

	/** Call the fail_detected_failure_marker symbol here
	 */
	public static void markDetectedFailure() {}
}
