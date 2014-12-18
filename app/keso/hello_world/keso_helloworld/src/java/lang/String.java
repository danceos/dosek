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

public class String {

	final private char[] value;

	final private static char[] NULL = new char[0];

	public String()
	{
		value = NULL;
	}

	public String(char[] newValue, int offset, int count)
	{
		value = new char[count];
		for(int i=0; i<count; i++) value[i] = newValue[offset+i];
	}

	public String(byte[] bytes, int offset, int length)
	{
		this(bytes, 0, offset, length);
	}

	public String(char[] newValue)
	{
		this(newValue, 0, newValue.length);
	}

	public String(byte[] newValue, int hibyte, int offset, int count)
	{
		int k = (hibyte & 0xFF) << 8;
		value = new char[count];
		for (int i = 0; i < count; i++)
			value[i] = (char)((newValue[offset + i] & 0xFF) + k);
	}

	public String(byte[] newValue, int hibyte)
	{
		this(newValue, hibyte, 0, newValue.length);
	}

	public String(byte[] newValue)
	{
		this(newValue, 0, 0, newValue.length);
	}

	public String(byte[] newValue, String enc)
	{
		this(newValue);
	}

	public String(String newValue)
	{
		int n = newValue.length();
		value = new char[n];
		newValue.getChars(0, n, value, 0);
	}

	public String(StringBuffer newValue)
	{
		int n = newValue.length();
		value = new char[n];
		newValue.getChars(0, n, value, 0);
	}

	public String(byte[] newValue, int hibyte, int offset, String encoding) {
		this(newValue, hibyte, offset, newValue.length );
	}

	public String toString()
	{
		return this;
	}

	public int hashCode()
	{
		int n = value.length;
		int sum = 0;
		int mult = 1;

		if (n <= 15)
		{
			for (int i = 0; i < n; i++)
			{
				sum += ((int) value[i]) * mult;
				mult *= 37;
			}
		}
		else
		{
			int k = n / 8;
			int m = n / k;
			int j = 0;
			for (int i = 0; i <= m && j < n; i++)
			{
				sum += ((int) value[j]) * mult;
				j += k;
				mult *= 39;
			}
		}

		return sum;
	}

	public int length()
	{
		return value.length;
	}

	public char charAt(int index)
	{
		return value[index];
	}

	public void getChars(int srcBegin, int srcEnd, char[] dst, int dstBegin)
	{
		if ((srcBegin < 0)
				|| (srcEnd > value.length)
				|| (srcEnd < srcBegin)
				|| (dst.length < (srcEnd - srcBegin + dstBegin)))
			throw out_of_bounds();
		charArrayCopy(value, srcBegin, dst, dstBegin, srcEnd - srcBegin);
	}

	public byte[] getBytes() {
		int len = this.length();
		byte[] buf = new byte[len];
		getBytes(0, len, buf, 0);
		return buf;
	}

	public byte[] getBytes(String enc) {
		return getBytes();
	}

	public void getBytes(int srcBegin, int srcEnd, byte[] dst, int dstBegin)
	{
		if (srcBegin < 0 || srcEnd > value.length || srcEnd < srcBegin)
			throw out_of_bounds();
		int count = srcEnd - srcBegin;
		for (int i = 0; i < count; i++)
			dst[dstBegin + i] = (byte) value[srcBegin + i];
	}

	public char[] toCharArray()
	{
		int len = value.length;
		char[] result = new char[len];
		for(int i=0; i<len; i++) result[i] = value[i];
		return result;
	}

	public String substring(int beginIndex)
	{
		if (beginIndex < 0 || beginIndex > value.length)
			throw out_of_bounds();
		return new String(value, beginIndex, value.length - beginIndex);
	}

	public String substring(int beginIndex, int endIndex)
	{
		if (beginIndex < 0 || endIndex > value.length || endIndex < beginIndex)
			throw out_of_bounds();
		return new String(value, beginIndex, endIndex - beginIndex);
	}

	public boolean equals(Object obj)
	{
		if (obj == null)
			return false;
		if (!(obj instanceof String))
			return false;

		String str = (String) obj;

		if (str.length() != this.value.length)
			return false;

		for (int i = 0; i < value.length; i++)
			if (str.value[i] != this.value[i])
				return false;

		return true;
	}

	public boolean equalsIgnoreCase(String str)
	{
		if (str == null)
			return false;

		if (str.length() != value.length)
			return false;

		for (int i = 0; i < value.length; i++)
		{
			char c1 = str.charAt(i);
			char c2 = value[i];
			if (c1 == c2)
				continue;
			if (Character.toUpperCase(c1) == Character.toUpperCase(c2))
				continue;
			if (Character.toLowerCase(c1) == Character.toLowerCase(c2))
				continue;
			return false;
		}

		return true;
	}

	public int compareTo(String str)
	{
		int n = Math.min(value.length, str.length());

		for (int i = 0; i < n; i++)
		{
			if (value[i] > str.charAt(i))
				return 1;
			if (value[i] < str.charAt(i))
				return -1;
		}

		if (value.length > n)
			return 1;
		if (str.length() > n)
			return -1;

		return 0;
	}

	public boolean regionMatches(boolean ignoreCase, int offset, String str, int strOffset, int len)
	{
		if (offset < 0 || offset + len > value.length)
			return false;
		if (strOffset < 0 || strOffset + len > str.length())
			return false;
		if (ignoreCase) {
			for (int i=0;i<len;i++) {
				char c1 = str.value[strOffset+i];
				char c2 = value[offset+i];
				if (c1 == c2)
					continue;
				if (Character.toUpperCase(c1) == Character.toUpperCase(c2))
					continue;
				if (Character.toLowerCase(c1) == Character.toLowerCase(c2))
					continue;
				return false;
			}
			return true;
		}
		return regionMatches(offset,str,strOffset,len);
	}

	public boolean regionMatches(int offset, String str, int strOffset, int len)
	{
		if (offset < 0 || offset + len > value.length)
			return false;
		if (strOffset < 0 || strOffset + len > str.length())
			return false;
		for (int i=0;i<len;i++) {
			if (value[offset+i]!=str.value[strOffset+i]) {
				return false;
			}
		}
		return true;
	}

	public boolean startsWith(String prefix)
	{
		int n = prefix.length();
		return regionMatches(0, prefix, 0, n);
	}

	public boolean startsWith(String prefix, int offset)
	{
		int n = prefix.length();
		return regionMatches(offset, prefix, 0, n);
	}

	public boolean endsWith(String suffix)
	{
		int n = suffix.length();
		return regionMatches(value.length - n, suffix, 0, n);
	}

	public String concat(String str)
	{
		int n = str.length();
		if (n == 0)
			return this;

		int m = value.length;
		char[] buff = new char[m + n];
		getChars(0, m, buff, 0);
		str.getChars(0, n, buff, m);

		return new String(buff);
	}

	public String replace(char oldChar, char newChar)
	{
		char[] buff = new char[value.length];
		boolean found = false;

		for (int i = 0; i < value.length; i++)
		{
			char c = value[i];
			if (c == oldChar)
			{
				found = true;
				buff[i] = newChar;
			}
			else
				buff[i] = c;
		}

		return found ? new String(buff) : this;
	}

	public String toLowerCase()
	{
		char[] buff = new char[value.length];
		for (int i = 0; i < value.length; i++)
			buff[i] = Character.toLowerCase(value[i]);
		return new String(buff);
	}

	public String toUpperCase()
	{
		char[] buff = new char[value.length];
		for (int i = 0; i < value.length; i++)
			buff[i] = Character.toUpperCase(value[i]);
		return new String(buff);
	}

	public String trim()
	{
		int i, j;

		for (i = 0; i < value.length; i++)
			if (value[i] > '\u0020')
				break;

		for (j = value.length - 1; j >= i; j--)
			if (value[j] > '\u0020')
				break;

		int n = j - i + 1;
		char[] buff = new char[n];
		charArrayCopy(value, i, buff, 0, n);

		return new String(buff);
	}

	public int indexOf(int c, int fromIndex)
	{
		for (int i = fromIndex; i < value.length; i++)
			if (value[i] == c)
				return i;
		return -1;
	}

	public int indexOf(int c)
	{
		return indexOf(c, 0);
	}

	public int indexOf(String str, int fromIndex)
	{
		int n = value.length - (str.length() - 1);
		for (int i = fromIndex; i < n; i++)
			if (startsWith(str, i))
				return i;
		return -1;
	}

	public int indexOf(String str)
	{
		return indexOf(str, 0);
	}

	public int lastIndexOf(int c, int fromIndex)
	{
		for (int i = value.length - 1; i >= fromIndex; i--)
			if (value[i] == c)
				return i;
		return -1;
	}

	public int lastIndexOf(int c)
	{
		return lastIndexOf(c, 0);
	}

	public int lastIndexOf(String str, int fromIndex)
	{
		for (int i = value.length - 1; i >= fromIndex; i--)
			if (startsWith(str, i))
				return i;
		return -1;
	}

	public int lastIndexOf(String str)
	{
		return lastIndexOf(str, 0);
	}

	public String intern()
	{
		/*	String str = (String) stringPool.get(this);
			if (str != null)
			return str;
			stringPool.put(this, this);
			*/
		return this;
	}

	public static String copyValueOf(char[] newValue)
	{
		return new String(newValue);
	}

	public static String copyValueOf(char[] newValue, int offset, int count)
	{
		return new String(newValue, offset, count);
	}

	public static String valueOf(boolean b)
	{
		return b ? "true" : "false";
	}

	public static String valueOf(char c)
	{
		char[] buf = new char[1];
		buf[0] = c;
		return new String(buf);
	}

	public static String valueOf(char[] newValue)
	{
		return new String(newValue);
	}

	public static String valueOf(char[] newValue, int offset, int count)
	{
		return new String(newValue, offset, count);
	}

	public static String valueOf(double d)
	{
		return Double.toString(d);
	}

	public static String valueOf(float f)
	{
		return Float.toString(f);
	}

	public static String valueOf(int i)
	{
		return Integer.toString(i);
	}

	public static String valueOf(long l)
	{
		return Long.toString(l);
	}

	public static String valueOf(Object obj)
	{
		return (obj == null) ? "null" : obj.toString();
	}

	private static void charArrayCopy(char[] src, int srcOffset, char[] dst, int dstOffset, int count) {
		for(int i=0; i<count; i++) {
			dst[dstOffset+i] = src[srcOffset+i];
		}
	}

	private StringIndexOutOfBoundsException out_of_bounds() {
		return new StringIndexOutOfBoundsException();
	}

	public String[] split(String regex) {
		throw new Error("not implemented");
	}
}
