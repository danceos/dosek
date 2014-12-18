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
package test;

import keso.core.TaskService;

public class HelloWorld implements Runnable {
	private long start,stop;
	public HelloWorld() {
		start = System.nanoTime();
		System.out.println("HelloWorld constructor\n");
	}

	private B aobj = new B();

	public void run() {
		System.out.println(System.getProperty("ddom1.ttask1.HelloString","Hello World!"));
		System.out.println("You successfully compiled and ran KESO. Goodbye...\n");

		int x = aobj.hashCode();
		while(true) { // trick jino in believing that the incremented value of x will be needed
			System.out.print("hash value: ");
			System.out.println((long) x);
			aobj.m2();

			stop = System.nanoTime();

			System.out.println("Runtime " + (stop-start) + " ns");
			System.out.println("\tstart: " + start + " ns");
			System.out.println("\tstop: " + stop + " ns");

			System.out.print("\thash value again: ");
			System.out.println(x++);
			TaskService.terminate();
		}
	}

}
