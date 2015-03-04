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

public final class Float extends Number {

	public static final Class	TYPE = Class.getPrimitiveClass("float");

	public static final float POSITIVE_INFINITY = 1.0f / 0.0f;
	public static final float NEGATIVE_INFINITY = -1.0f / 0.0f;
	public static final float NaN = 0.0f / 0.0f;
	public static final float MAX_VALUE = 3.40282346638528860e+38f;
	public static final float MIN_VALUE = 1.40129846432481707e-45f;

	private float value;

	public Float(float value) {
		this.value = value;
	}

	public Float(double value) {
		this.value = (float)value;
	}

	public byte byteValue() {
		return (byte)value;
	}

	public double doubleValue() {
		return (double)value;
	}

	public boolean equals(Object obj) {
		 return (obj != null) && (obj instanceof Float) && (floatToIntBits(((Float)obj).value) == floatToIntBits(value));
	}

	public static int floatToIntBits(float value) {
		return 0; // KNI
	}

	public float floatValue() {
		return value;
	}

	public int hashCode() {
		return floatToIntBits(value);
	}

	public static float intBitsToFloat(int bits) {
 		return 0.0f;
	}

	public int intValue() {
		return (int)value;
	}

	public boolean isInfinite() {
		return isInfinite(value);
	}

	static public boolean isInfinite(float v) {
		return (v == POSITIVE_INFINITY) || (v == NEGATIVE_INFINITY);
	}

	public boolean isNaN() {
		return isNaN(value);
	}

	static public boolean isNaN(float v) {
		return (v != v);
	}

	public long longValue() {
		return (long)value;
	}

	public static float parseFloat(java.lang.String s) {
		throw new Error("not implemented");
	}

	public short shortValue() {
		return (short)value;
	}

	public String toString() {
		return String.valueOf(value);
	}

	public static String toString(float f){
		return Double.toString((double) f);
	}

	public static Float valueOf(float f) {
		return new Float(f);
	}

	public static Float valueOf(String s) throws NumberFormatException {
		return new Float(Double.valueOf0(s));
	}

	public Float(String s) throws NumberFormatException {
		// REMIND: this is inefficient
		this(valueOf(s).floatValue());
	}

	// not CLDC
	public static int compare(float a, float b) {throw new Error("not implemented");}
}
