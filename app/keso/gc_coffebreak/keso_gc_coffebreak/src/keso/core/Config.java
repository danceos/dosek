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
 * The Config class allows Java applications to get values
 * specified in the kesorc configuration file.
 *
 * The configuration properties are references by their name,
 * and accesses are resolved at compile time. Therefore, only
 * String constants may be specified in all methods of this class.
 *
 * The KESO configuration is a tree of sets. Each set contains either
 * other sets or configuration properties. The leaves of the tree do
 * only contain properties. The root set is the Systemdefinition.
 * The currently existing set Types are
 *
 *   a  Alarm
 *   c  Counter
 *   d  Domain
 *   e  Event
 *   h  Heap
 *   i  ISR
 *   m  AppMode
 *   o  OSEKOS Definition
 *   r  Resource
 *   t  Task
 *
 * Name parameters to all methods need to be specified as fully qualified
 * identifiers, starting from the System configuration, in the Form
 * &lt;SetTypeLetter&gt;SetName.&lt;SetTypeLetter&gt;SetName.property
 *
 * The Value will be literally inserted, to be sure that the property is
 * of the correct type or the generated C-Code will not compile.
 * <p>
 * Example:<br>
 *  <i>ddriver.iserialhnd.baudrate</i>
 *   will insert the baudrate property specified for the ISR serialhnd
 *   of the domain driver.
 */
public final class Config {

	/**
	 * Insert a byte value form the config file.
	 *
	 * @param name property name
	 *
	 * @param dflt default value which ist used if the property is not
	 *       in the config file.
	 */
	public static byte   getByte  (String name, byte dflt)    { return 0; }
	public static char   getChar  (String name, char dflt)    { return 0; }
	public static short  getShort (String name, short dflt)    { return 0; }
	public static int    getInt   (String name, int dflt)    { return 0; }
	public static long   getLong  (String name, long dflt)    { return 0; }

	public static float  getFloat (String name, float dflt)    { return 0; }
	public static double getDouble(String name, double dflt)    { return 0; }

	public static String getString(String name, String dflt)    { return null; }

	public static int[] getIntArray(String name)    { return null; }
	public static short[] getShortArray(String name)    { return null; }
}
