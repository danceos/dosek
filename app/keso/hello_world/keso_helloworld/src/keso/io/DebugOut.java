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
package keso.io;

/**
 * Small class for buffered debug output.
 */
final public class DebugOut {

	private final static StringBuilder buf = new StringBuilder();

	public static void print(double value) {
		buf.append(Double.toString(value));
	}

	public static void print(float value) {
		buf.append(Float.toString(value));
	}

	public static void print(long value) {
		buf.append(Long.toString(value));
	}

	public static void print(int value) {
		buf.append(Integer.toString(value));
	}

	public static void print(char value) {
		buf.append(value);
	}

	public static void print(String msg) {
		buf.append(msg);
	}

	public static void print(StringBuffer msg) {
		buf.append(msg);
	}

	public static void print(char[] msg) {
		buf.append(msg);
	}

	public static void print(Object msg) {
		buf.append(msg.toString());
	}

	public static void println(double value) {
		println(Double.toString(value));
	}

	public static void println(float value) {
		println(Float.toString(value));
	}

	public static void println(long value) {
		println(Long.toString(value));
	}

	public static void println(int value) {
		println(Integer.toString(value));
	}

	public static void println(char value) {
		buf.append(value);
		println();
	}

	public static void println(String msg) {
		buf.append(msg);
		println();
	}

	public static void println(Object msg) {
		buf.append(msg.toString());
		println();
	}

	public static void println(StringBuffer msg) {
		buf.append(msg);
		println();
	}

	public static void println(char[] msg) {
		buf.append(msg);
		println();
	}

	public static void println() {
		StringBuilder b = buf;
		b.append("\r\n");
		raw_print(b);
		b.setLength(0);
	}

	public static void flush() {
		raw_print(buf);
		buf.setLength(0);
	}

	private static void raw_print(StringBuilder msg) {
		/* we do nothing here! */
	}
}
