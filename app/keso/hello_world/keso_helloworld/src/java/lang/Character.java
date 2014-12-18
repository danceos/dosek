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

public final class Character
{
	public static final char MIN_VALUE = 0;
	public static final char MAX_VALUE = 255;
	public static final int MIN_RADIX = 2;
	public static final int MAX_RADIX = 36;

	//public static final Class TYPE = Class.getPrimitiveClass("char");

	private char value;

	public Character(char value) { this.value = value; }

	public String toString() {
		return String.valueOf(value);
	}

	public boolean equals(Object obj) {
		if (obj == null || !(obj instanceof Character))
			return false;
		return ((Character)obj).value == value;
	}

	public int hashCode() { return (int) value; }

	public char charValue() { return value; }

	public static boolean isDefined(char ch) { return true; }

	public static boolean isWhitespace(char ch) {
		if (ch==' ') return true;
		if (ch=='\t') return true;
		return false;
	}

	public static boolean isLowerCase(char ch) {
		if(ch>='a' && ch<='z') return true;
		return false;
	}

	public static boolean isUpperCase(char ch) {
		if(ch>='A' && ch<='Z') return true;
		return false;
	}

	public static boolean isTitleCase(char ch) { return false; }

	public static boolean isDigit(char ch) {
		if(ch>='0' && ch<='9') return true;
		return false;
	}

	public static boolean isLetter(char ch) {
		if((ch>='a' && ch<='z') || (ch>='A' && ch<='Z'))
			return true;
		return false;
	}

	public static boolean isLetterOrDigit(char ch) {
		return (isLetter(ch) || isDigit(ch));
	}

	public static boolean isJavaLetter(char ch) {
		return (ch=='_' || ch=='$' || isLetter(ch));
	}

	public static boolean isJavaLetterOrDigit(char ch) {
		return (isJavaLetter(ch) || isDigit(ch));
	}

	public static char toTitleCase(char ch) { return ch; }

	public static int digit(char ch, int radix) {
		if (radix < MIN_RADIX || radix > MAX_RADIX)
			return -1;

		if (isDigit(ch)) {
			int d = (ch - '0');
			return (d < radix) ? d : -1;
		}

		if (ch >= 'A' && ch < (char)('A' + radix - 10))
			return (ch - 'A' + 10);
		if (ch >= 'a' && ch < (char)('a' + radix - 10))
			return (ch - 'a' + 10);
		return -1;
	}

	public static char forDigit(int digit, int radix) {
		if(radix < MIN_RADIX || radix > MAX_RADIX)
			return MIN_VALUE;
		if(digit < 0 || digit >= radix)
			return MIN_VALUE;
		if (digit < 10)
			return (char)('0' + digit);
		else
			return (char)('a' + digit - 10);
	}

	public static boolean isSpace(char ch) {
		switch (ch) {
			case '\t':
			case '\n':
			case '\f':
			case '\r':
			case ' ':
				return true;
			default:
				return false;
		}
	}

	public static char toLowerCase(char ch) {
		if(isUpperCase(ch))
			return (char)('a' - 'A' + ch);
		return ch;
	}

	public static char toUpperCase(char ch) {
		if(isLowerCase(ch))
			return (char)(ch - 'a' + 'A');
		return ch;
	}

	public static Character valueOf(char c) {
		return new Character(c);
	}

}
