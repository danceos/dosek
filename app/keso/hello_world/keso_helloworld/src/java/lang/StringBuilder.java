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

public class StringBuilder {

	private char[] data;
	private int length; // actual used bytes in the string
	private final static int minIncrease=8;
	private final static int maxIncrease=32;

	public StringBuilder(int length) {
		data = new char[length];
		this.length = 0;
	}

	public StringBuilder(String str) {
		this(str.length() + minIncrease);
		append(str);
	}

	public StringBuilder() {
		this(minIncrease);
	}

	public int length() { return length; }

	public int capacity() { return data.length; }

	public void ensureCapacity(int minimumCapacity) {
		if (data.length >= minimumCapacity) return;
		int d = Math.min(maxIncrease,data.length << 1);
		int n = Math.max(minimumCapacity, d);
		char[] buff = new char[n];
		copy_chars(data, 0, buff, 0, data.length);
		data = buff;
	}

	public String toString() {
		return new String(data, 0, length);
	}

	public char charAt(int index) {
		if (index < 0 || index >= length)
			throw new StringIndexOutOfBoundsException();
		return data[index];
	}

	public void getChars(int srcBegin, int srcEnd, char[] dst, int dstBegin) {
		if (srcBegin < 0 || srcEnd >= length || srcEnd < srcBegin)
			throw new StringIndexOutOfBoundsException();
		copy_chars(data, srcBegin, dst, dstBegin, srcEnd - srcBegin);
	}

	public void setCharAt(int index, char c) {
		if (index < 0 || index >= length)
			throw new StringIndexOutOfBoundsException();
		data[index] = c;
	}

	public void setLength(int newLength) {
		ensureCapacity(newLength);
		if(newLength > length) {
			 for (int i = length; i < newLength; i++)
				  data[i] = '\u0000';
		}
		else {
			 data[newLength] = '\u0000';
		}
		length = newLength;
	}

	public StringBuilder reverse() {
		for (int i = 0; i < length / 2; i++) {
			int j = length - 1 - i;
			char tmp = data[i];
			data[i] = data[j];
			data[j] = tmp;
		}
		return this;
	}

	public StringBuilder append(char c) {
		ensureCapacity(length + 1);
		data[length] = c;
		length++;
		return this;
	}

	public StringBuilder append(char[] str, int offset, int len) {
		ensureCapacity(length + len);
		copy_chars(str, offset, data, length, len);
		length += len;
		return this;
	}

	public StringBuilder append(char[] str) {
		return append(str, 0, str.length);
	}

	public StringBuilder append(Object obj) {
		if (obj == null)
			return append("null");
		return append(obj.toString());
	}

	public StringBuilder append(String str) {
		if (str == null)
			return append("null");

		int n = str.length();
		ensureCapacity(length + n);
		str.getChars(0, n, data, length);
		length += n;

		return this;
	}

	public StringBuilder append(StringBuilder str) {
		if (str == null)
			return append("null");

		int n = str.length();
		ensureCapacity(length + n);
		str.getChars(0, n, data, length);
		length += n;

		return this;
	}

	public StringBuilder append(boolean b) {
		return append(String.valueOf(b));
	}

	public StringBuilder append(int i) {
		return append(Integer.toString(i));
	}

	public StringBuilder append(long l) {
		return append(Long.toString(l));
	}

	public StringBuilder append(float f) {
		return append(String.valueOf(f));
	}

	public StringBuilder append(double d) {
		return append(String.valueOf(d));
	}

	private void insertGap(int offset, int n) {
		ensureCapacity(length + n);
		if (offset < length)
			copy_chars(data, offset, data, offset + n, length - offset);
	}

	public StringBuilder insert(int offset, char c) {
		if (offset < 0 || offset > length)
			throw new StringIndexOutOfBoundsException();
		insertGap(offset, 1);
		data[offset] = c;
		length++;
		return this;
	}

	public StringBuilder insert(int offset, char[] str) {
		if (offset < 0 || offset > length)
			throw new StringIndexOutOfBoundsException();
		int n = str.length;
		insertGap(offset, n);
		copy_chars(str, 0, data, offset, n);
		length += n;
		return this;
	}

	public StringBuilder insert(int offset, String str) {
		if (offset < 0 || offset > length)
			throw new StringIndexOutOfBoundsException();
		int n = str.length();
		insertGap(offset, n);
		str.getChars(0, n, data, offset);
		length += n;
		return this;
	}

	public StringBuilder insert(int offset, boolean b) {
		return insert(offset, String.valueOf(b));
	}

	public StringBuilder insert(int offset, int i) {
		return insert(offset, String.valueOf(i));
	}

	public StringBuilder insert(int offset, long l) {
		return insert(offset, String.valueOf(l));
	}

	public StringBuilder insert(int offset, float f) {
		return insert(offset, String.valueOf(f));
	}

	public StringBuilder insert(int offset, double d) {
		return insert(offset, String.valueOf(d));
	}

	public StringBuilder insert(int offset, Object o) {
		return insert(offset, String.valueOf(o));
	}

	public StringBuilder delete(int start, int end) {
		if (start > end || start < 0 || start >= length)
			throw new StringIndexOutOfBoundsException();
		if (start == end)
			return this;
		if (end < length)
			copy_chars(data, end, data, start, length - end);
		setLength(length - (end - start));
		return this;
	}

	 public StringBuilder deleteCharAt(int index) {
		  if(index > length-1 || index < 0)
				throw new StringIndexOutOfBoundsException();
		  if(index < length-1)
				copy_chars(data, index+1, data, index, length - index - 1);
		  setLength(length - 1);
		  return this;
	 }

	public StringBuilder replace(int start, int end, String str) {
		delete(start, end);
		insert(start, str);
		return this;
	}

	private static void copy_chars(char[] src, int srcOffset, char[] dst, int dstOffset, int count) {
		for(int i=0; i<count; i++) dst[dstOffset+i] = src[srcOffset+i];
	}
}
