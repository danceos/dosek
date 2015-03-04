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

//import java.io.InputStream;
import java.io.PrintStream;
import java.io.InputStream;
import keso.io.DebugOutPrintStream;
import keso.io.NullPrintStream;

public class System {

	public static InputStream in= null;
	public static PrintStream out;
	public static PrintStream err;

	static {
		if(keso.core.Config.getInt("jino.no_write", 0) == 0) {
			out = err = new DebugOutPrintStream();
		} else {
			out = err = new NullPrintStream();
		}
	}

	public static void arraycopy(Object src, int srcOffset, Object dst, int dstOffset, int count) {
		if( src == dst && dstOffset > srcOffset ){
			if (src instanceof byte[] && dst instanceof byte[]) {
				arraycopy_byte_left((byte[])src,srcOffset,(byte[])dst,dstOffset,count);
			} else if (src instanceof char[] && dst instanceof char[]) {
				arraycopy_char_left((char[])src,srcOffset,(char[])dst,dstOffset,count);
			} else {
				arraycopy_left((Object[])src,srcOffset,(Object[])dst,dstOffset,count);
			}
		} else {
			if (src instanceof byte[] && dst instanceof byte[]) {
				arraycopy_byte_right((byte[])src,srcOffset,(byte[])dst,dstOffset,count);
			} else if (src instanceof char[] && dst instanceof char[]) {
				arraycopy_char_right((char[])src,srcOffset,(char[])dst,dstOffset,count);
			} else {
				arraycopy_right((Object[])src,srcOffset,(Object[])dst,dstOffset,count);
			}
		}
	}

	public static void exit(int status) {
		keso.core.OSService.shutdownOS(status);
	}

	public static void gc() { }

	public static void load(String filename) { }

	public static void loadLibrary(String libname) { }

	public static String getProperty(String key, String def) {
		return null;
	}

	public static String getProperty(String key) {
		return null;
	}

	/**
	 * Returns the current time in milliseconds. Note that while the unit of time
	 * of the return value is a millisecond, the granularity of the value depends on
	 * the underlying operating system and may be larger. For example, many operating
	 * systems measure time in units of tens of milliseconds.
	 *
	 * See the description of the class Date for a discussion of slight discrepancies that may arise
	 * between "computer time" and coordinated universal time (UTC). *
	 * Returns:
	 * the difference, measured in milliseconds, between the current time and
	 * midnight, January 1, 1970 UTC.
	 */
	public static long currentTimeMillis() {
		return nanoTime() / 1000000L;
	}

 	/* implemented by NanoTimeWeavelet */
	public static long nanoTime() {
  	return 0L;
  }

	public static int identityHashCode(Object obj) { return obj.hashCode(); }

 	/* byte[] */
	private static void arraycopy_byte_left(byte[] src, int srcOffset, byte[] dst, int dstOffset, int count) {
		srcOffset += count; dstOffset += count;
		for(int i=0; i<count; ++i) dst[--dstOffset] = src[--srcOffset];
	}

	private static void arraycopy_byte_right(byte[] src, int srcOffset, byte[] dst, int dstOffset, int count) {
		for(int i=0; i<count; i++) dst[dstOffset+i] = src[srcOffset+i];
	}

	/* char[] */
	private static void arraycopy_char_left(char[] src, int srcOffset, char[] dst, int dstOffset, int count) {
		srcOffset += count; dstOffset += count;
		for(int i=0; i<count; ++i) dst[--dstOffset] = src[--srcOffset];
	}

	private static void arraycopy_char_right(char[] src, int srcOffset, char[] dst, int dstOffset, int count) {
		for(int i=0; i<count; i++) dst[dstOffset+i] = src[srcOffset+i];
	}

	/* else */
	private static void arraycopy_left(Object[] src, int srcOffset, Object[] dst, int dstOffset, int count) {
		srcOffset += count; dstOffset += count;
		for(int i=0; i<count; ++i) dst[--dstOffset] = src[--srcOffset];
	}

	private static void arraycopy_right(Object[] src, int srcOffset, Object[] dst, int dstOffset, int count) {
		for(int i=0; i<count; i++) dst[dstOffset+i] = src[srcOffset+i];
	}

	public static void setIn(InputStream in) {
		throw new Error("Not implemented!");
	}

}
