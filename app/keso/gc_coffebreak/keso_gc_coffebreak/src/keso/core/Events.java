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
 * This class only contains definitions of the masks for every event that
 * may be used in the Java application just as they would be used in C programs.
 */

/*
 * The KESO_INSERT_DEFINITIONS comment is a special placeholder that will be
 * substituted by the builder with the actual event definitions. Do not
 * remove/change this line.
 */
public final class Events {
	private Events() {}

	public static final int Wakeup = 0x1;

}
