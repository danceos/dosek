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

import keso.core.Task;
import keso.core.TaskService;

public class TestStaticField implements Runnable {
	private static Object obj;

	public void run() {
		int c=20000;
		int step=0;

		// Allocated here because writing local
		// variables does not use a writebarrier
		Object x = new StringBuffer(5);
		Object y = new StringBuffer(10);
		Object z = new StringBuffer(15);

		while(c-->0) {
			step++;
			switch(step) {
				case 1:
					obj=x;
					break;
				case 2:
					obj=y;
					break;
				default:
					obj=z;
					step=0;
			}
		}
	}
}
