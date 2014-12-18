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
package java.io;

public class PrintStream extends FilterOutputStream {

	final static private boolean autoflush = true;

	private boolean error = false;

	public PrintStream(OutputStream o) {
		super(o);
	}

	public boolean checkError() {
		return error;
	}

	public void close() {
		try {
			out.close();
		} catch (IOException e) {
			error = true;
		}
	}

	public void flush() {
		try {
			out.flush();
		} catch (IOException e) {
			error = true;
		}
	}

	public void write(int b) {
		try {
			out.write(b);
		} catch (IOException e) {
			error = true;
		}

		if (autoflush && b == '\n')
			flush();
	}

	public  void write(byte[] b, int off, int len) {
		try {
			out.write(b, off, len);
		} catch (IOException e) {
			error = true;
		}

		if (!autoflush)
			return;

		for (int i = 0; i < b.length; i++) {
			if (b[i] != '\n')
				continue;

			flush();
			break;
		}
	}

	public void print(char[] s) {
		for (int i = 0; i < s.length; i++)
			write((int) s[i]);
	}

	public void print(String s) {
		int len = s.length();
		byte[] buff = new byte[len];
		s.getBytes(0, len, buff, 0);
		write(buff, 0, len);
	}

	public void print(boolean v) {
		print(v ? "true" : "false");
	}

	public void print(char v) {
		write((int) v);
	}

	public void print(float v) {
		print(Float.toString(v));
	}

	public void print(double v) {
		print(Double.toString(v));
	}

	public void print(int v) {
		print(Integer.toString(v));
	}

	public void print(long v) {
		print(Long.toString(v));
	}

	public  void print(Object v) {
		print(v == null ? "null" : v.toString());
	}

	public void println() {
		write('\n');
	}

	public  void println(char[] s) {
		print(s);
		println();
	}

	public  void println(String s) {
		print(s);
		println();
	}

	public  void println(boolean v) {
		print(v);
		println();
	}

	public  void println(char v) {
		print(v);
		println();
	}

	public  void println(int v) {
		print(v);
		println();
	}

	public  void println(long v) {
		print(v);
		println();
	}

	public  void println(float v) {
		print(v);
		println();
	}

	public  void println(double v) {
		print(v);
		println();
	}

	public  void println(Object v) {
		print(v);
		println();
	}
}
