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

public final class Long extends Number
{
	public static final Class TYPE = Class.getPrimitiveClass("long");
	public static final long MIN_VALUE = 0x8000000000000000L;
	public static final long MAX_VALUE = 0x7FFFFFFFFFFFFFFFL;

	private long value;

	public Long(long value) {
		this.value = value;
	}

	public Long(String s) throws NumberFormatException {
	 	this.value = parseLong(s);
	}

	public double doubleValue() {
		return (double) value;
	}

	public boolean equals(Object obj) {
		if (obj == null)
			return false;
		if (!(obj instanceof Long))
			return false;

		Long l = (Long) obj;
		return value == l.longValue();
	}

	public float floatValue() {
		return (float) value;
	}

	public int hashCode() {
		return (int)(value ^ (value >>> 32));
	}

	public long longValue() {
		return (long) value;
	}

	public static long parseLong(String s) throws NumberFormatException {
		return parseLong(s, 10);
	}

	public static long parseLong(String s, int radix) throws NumberFormatException {
		if (s == null || s.equals(""))
			throw new NumberFormatException();

		if (radix < Character.MIN_RADIX || radix > Character.MAX_RADIX)
			throw new NumberFormatException();

		int position = 0;
		long result = 0;
		boolean signed = false;

		if (s.charAt(position) == '-')
		{
			signed = true;
			position++;
		}

		int digit;

		for (; position < s.length(); position++)
		{
			digit = Character.digit(s.charAt(position), radix);
			if (digit < 0)
				throw new NumberFormatException();
			result = (result * radix) - digit;
		}

		if (!signed && result < -MAX_VALUE)
			throw new NumberFormatException();

		return (signed ? result : -result );
	}

	public String toString() {
		return toString(value);
	}

	public static String toString(long value) {
		return toString(value, 10);
	}

	public static String toString(long value,int radix) {
		final char buffer[] = new char[20]; // max len (radix 10!!!): -9223372036854775808
		int i=20;

//		buffer[--i]='L';
		if (value == 0) {
			buffer[--i]='0';
			return new String(buffer, i, 20-i);
		}

		boolean isNegative = false;
		if( value < 0 ){
			isNegative = true;
			value = -value;
		}

		while (value > 0) {
			int r = (int)(value % radix);
			buffer[--i]=Character.forDigit(r, radix);
			value /= radix;
		}

		if (isNegative) buffer[--i]='-';

		return new String(buffer, i, 20-i);
	}

	private static String toUnsignedString(long value, int shift) {
		if( value == 0 )
			return "0";

		String result = "";
		int radix = 1 << shift;
		int mask = radix - 1;
		while (value != 0)
		{
			result = Character.forDigit((int)(value & mask), radix) + result;
			value >>>= shift;
		}
		return result;
	}


	public static String toHexString(long i) {
		return toUnsignedString(i, 4);
	}

	public static String toOctalString(long i) {
		return toUnsignedString(i, 3);
	}

	public static String toBinaryString(long i) {
		return toUnsignedString(i, 1);
	}

	public static Long valueOf(String s) throws NumberFormatException {
		return new Long(parseLong(s));
	}

	public static Long valueOf(long l) {
		return new Long(l);
	}

	public static Long valueOf(String s, int radix) throws NumberFormatException {
		return new Long(parseLong(s, radix));
	}

	public static Long getLong(String nm) {
		return getLong(nm, null);
	}

	public static Long getLong(String nm, long val) {
		Long result = getLong(nm, null);
		return ((result == null) ? new Long(val) : result);
	}

	public static Long getLong(String nm, Long val) {
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

	public int intValue() {
		return (int) value;
	}
}
