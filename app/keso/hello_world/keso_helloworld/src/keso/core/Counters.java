/**(c)

  Copyright (C) 2006-2012 Christian Wawersich, Michael Stilkerich, Christoph Erhardt

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

package keso.core;

/**
 * This class contains the OSEK counter constants. These are the return values
 * of GetAlarmBase. Calls to GetAlarmBase can be spared if the name of the
 * underlying counter is known.
 */
public final class Counters {
	private Counters() {}

	public static final int OSTICKSPERBASE_sysCounter = 0x1;
	public static final int OSMAXALLOWEDVALUE_sysCounter = 0xffff;
	public static final int OSMINCYCLE_sysCounter = 0x1;

	public static final int OSTICKSPERBASE = 0x1;
	public static final int OSMAXALLOWEDVALUE = 0xffff0001;
	public static final int OSMINCYCLE = 0x1;
	public static final int OSTICKDURATION = 0x0;

}
