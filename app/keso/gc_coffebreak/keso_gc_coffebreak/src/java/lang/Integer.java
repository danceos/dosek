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

public class Integer extends Number {
	public static final Class TYPE = Class.getPrimitiveClass("int");

	public static final int MIN_VALUE = 0x80000000;
	public static final int MAX_VALUE = 0x7FFFFFFF;

	private int value;

	public Integer(int value) { this.value = value; }

	public Integer(String s) throws NumberFormatException {
		value = parseInt(s);
	}

	public byte byteValue() {
		return (byte) value;
	}

	public double doubleValue() {
		return (double)value;
	}

	public boolean equals(Object obj) {
		if(obj != null && obj instanceof Integer) {
			return (value == ((Integer)obj).value);
		}
		return false;
	}

	public float floatValue() {
		return (float)value;
	}

	public int hashCode() { return value; }

	public int intValue() { return value; }

	public long longValue() { return (long)value; }

	public static int parseInt(String s) throws NumberFormatException {
		return parseInt(s, 10);
	}

	public static int parseInt(String s, int radix) throws NumberFormatException {
		if (s == null || s.equals("")) throw new NumberFormatException();
		if (radix < Character.MIN_RADIX || radix > Character.MAX_RADIX)
			throw new NumberFormatException();

		int position = 0;
		int result = 0;
		boolean sign = false;
		if (s.charAt(position) == '-') {
			sign = true;
			position++;
		}
		int digit;

		for (; position < s.length(); position++) {
			digit = Character.digit(s.charAt(position), radix);
			if (digit < 0) throw new NumberFormatException();
			result = (result * radix) - digit;
		}

		if (!sign && result < -MAX_VALUE) throw new NumberFormatException();
		return (sign ? result : -result );
	}

	public short shortValue() {
		return (short) value;
	}

	public static String toBinaryString(int i) {
		return toUnsignedString(i, 1);
	}

	public static String toHexString(int i) {
		return toUnsignedString(i, 4);
	}

	public static String toOctalString(int i) {
		return toUnsignedString(i, 3);
	}

	public String toString() { return toString(value); }

	public static String toString(int i) {
		return toString(i, 10);
	}

	public static String toString(int value, int radix) {
		StringBuilder buffer = new StringBuilder(10);
		boolean isNegative = false;

		if (value == 0) {
			buffer.append('0');
			return buffer.toString();
		}

		if( value < 0 ) {
			isNegative = true;
			value = -value;
		}

		while (value > 0){
			buffer.append(Character.forDigit(value % radix, radix));
			value /= radix;
		}

		if (isNegative) buffer.append('-');

		buffer.reverse();

		return buffer.toString();
	}

	public static Integer valueOf(int i) {
		return new Integer(i);
	}

	public static Integer valueOf(String s) throws NumberFormatException {
		return new Integer(parseInt(s));
	}

	public static Integer valueOf(String s, int radix) throws NumberFormatException {
		return new Integer(parseInt(s, radix));
	}

	private static String toUnsignedString(int value, int shift) {
		if(value == 0) return "0";

		String result = "";
		int radix = 1 << shift;
		int mask = radix - 1;
		while (value != 0) {
			result = Character.forDigit(value & mask, radix) + result;
			value >>>= shift;
		}
		return result;
	}

	public static Integer getInteger(String nm) {
		return getInteger(nm, null);
	}

	public static Integer getInteger(String nm, int val) {
		Integer result = getInteger(nm, null);
		return ((result == null) ? new Integer(val) : result);
	}

	public static Integer getInteger(String nm, Integer val) {
/* TODO:
	String value = System.getProperty(nm);
	if (value == null)
	    return val;
	try
	    {
		if (value.startsWith("0x"))
		    return valueOf(value.substring(2), 16);
		if (value.startsWith("#"))
		    return valueOf(value.substring(1), 16);
		if (value.startsWith("0"))
		    return valueOf(value.substring(1), 8);
		return valueOf(value, 10);
	    }
	catch (NumberFormatException ex)
	    {
	    }
*/
	return val;
	}
}
