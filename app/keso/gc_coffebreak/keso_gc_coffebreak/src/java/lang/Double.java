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

package java.lang;

public final class Double extends Number {

	public static final Class	TYPE = Class.getPrimitiveClass("double");

	public static final double POSITIVE_INFINITY = 1.0 / 0.0;
	public static final double NEGATIVE_INFINITY = -1.0 / 0.0;
	public static final double NaN = 0.0d / 0.0;
	public static final double MAX_VALUE = 1.79769313486231570e+308;
	public static final double MIN_VALUE = 4.94065645841246544e-324;

	private double value;

	public Double(double a) {
		value = a;
	}

	public byte byteValue() {
		return (byte)value;
	}

	public static long doubleToLongBits(double value) {
		return 0; // done by KNI
	}

	public double doubleValue() {
		return (double)value;
	}

	public boolean equals(Object obj) {
		return (obj != null)
			&& (obj instanceof Double)
			&& (doubleToLongBits(((Double)obj).value) ==
					doubleToLongBits(value));
	}

	public float floatValue() {
		return (float)value;
	}

	public int hashCode() {
		long bits = doubleToLongBits(value);
		return (int)(bits ^ (bits >> 32));
	}

	public int intValue() {
		return (int)value;
	}

	public boolean isInfinite() {
		return isInfinite(value);
	}

	static public boolean isInfinite(double v) {
		return (v == POSITIVE_INFINITY) || (v == NEGATIVE_INFINITY);
	}

	public boolean isNaN() {
		return isNaN(value);
	}

	static public boolean isNaN(double v) {
		return (v != v);
	}

	public static double longBitsToDouble(long bits) {
		return 0.0f; // KNI
	}

	public long longValue() {
		return (long)value;
	}

	public static double parseDouble(java.lang.String s) { throw new Error("not implemented"); }

	public short shortValue() {
		return (short)value;
	}

	public String toString() {
		return toString(value);
	}

	public static String toString(double d) {
		return ""; // done by KNI
	}

	public Double(String s) throws NumberFormatException {
		// REMIND: this is inefficient
		this(valueOf(s).doubleValue());
	}

	public static Double valueOf(double d) {
		return new Double(d);
	}

	public static Double valueOf(String s) throws NumberFormatException {
		return new Double(valueOf0(s));
	}

	static double valueOf0(String s) throws NumberFormatException{
		return 0.0; // KNI
	}

	// not in CLDC
	public static int compare(double a, double b) {throw new Error("not implemented");}
}
