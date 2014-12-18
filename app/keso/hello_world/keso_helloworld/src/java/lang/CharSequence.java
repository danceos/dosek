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

public interface CharSequence {
	/**
	 * Get the char at the specified index. Valid values for index range from
	 * 0 to {@code length() - 1}.
	 *
	 * @param index the index of the character that is to be returned
	 * @return the character at the position identified by index
	 */
	public char charAt(int index);

	/**
	 * Calculate and return the length of the character sequence.
	 *
	 * @return an integer describing the length of the char sequence.
	 */
	public int length();

	/**
	 * Access a subsequence of the current character sequence. The new
	 * subsequence starts at index {@code start} and ends at index {@code end
	 * - 1}.
	 *
	 * @param start the start index, inclusive
	 * @param end the end index, exclusive
	 * @return a new character sequence that is the subsequence from start to
	 *         (end - 1) of this sequence
	 */
	public CharSequence subSequence(int start, int end);

	/**
	 * Return a String representation of this CharacterSequence.
	 *
	 * @return a string containing the characters in this sequence
	 */
	public String toString();
}
