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

import keso.io.DebugOut;

public class QueueElement {
	private QueueElement next;
	private final int value;

	public QueueElement(int value) {
		this.value = value;
		next = null;
	}

	protected void finalize() {
//		if((value % 20)==0) {
			DebugOut.print("Freed QEL ");
			DebugOut.println(value);
//		}
	}

	public int value() { return value; }
	public QueueElement next() { return next; }
	public void next(QueueElement qel) { next = qel; }
}
