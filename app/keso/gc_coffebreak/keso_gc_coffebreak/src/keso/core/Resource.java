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
 *	System object class for OSEK resources.
 *
 *	Resources are defined in the KESORC system configuration file. For each
 *	resource specified therein, a system object that is an instance of this
 *	class is created by the compiler.
 *
 *	The application cannot create instances of this class itself.
 *
 *	To access the system object of a resource, you need to use the
 *	{@link ResourceService#getResourceByName(String)} method.
 */
public final class Resource implements NonCopyable {
	private Resource() {	}
}
