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

import java.io.PrintStream;
import java.io.IOException;

public final class DebugOutPrintStream extends PrintStream {
	private static final DebugOutOutputStream os = new DebugOutOutputStream();

	public DebugOutPrintStream() { super(os); }

	public boolean checkError() { return false; }

	public void print(char[] s) {
		DebugOut.print(s);
	}

	public void print(String s) {
		DebugOut.print(s);
	}

	public void print(boolean v) {
		DebugOut.print(v);
	}

	public void print(char v) {
		DebugOut.print(v);
	}

	public void print(float v) {
		DebugOut.print(v);
	}

	public void print(double v) {
		DebugOut.print(v);
	}

	public void print(int v) {
		DebugOut.print(v);
	}

	public void print(long v) {
		DebugOut.print(v);
	}

	public void print(Object v) {
		DebugOut.print(v);
	}

	public void println() {
		DebugOut.println();
	}

	public  void println(char[] s) {
		DebugOut.println(s);
	}

	public  void println(String s) {
		DebugOut.println(s);
	}

	public  void println(boolean v) {
		DebugOut.println(v);
	}

	public  void println(char v) {
		DebugOut.println(v);
	}

	public  void println(int v) {
		DebugOut.println(v);
	}

	public  void println(long v) {
		DebugOut.println(v);
	}

	public  void println(float v) {
		DebugOut.println(v);
	}

	public  void println(double v) {
		DebugOut.println(v);
	}

	public  void println(Object v) {
		DebugOut.println(v);
	}
}
