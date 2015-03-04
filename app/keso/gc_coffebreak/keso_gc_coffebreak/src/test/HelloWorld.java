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

import keso.core.*;
import keso.io.DebugOut;

public class HelloWorld implements ListPrintService,Runnable {
	private int runs = 0;

	public void printList(QueueElement qel) {
		DebugOut.print("\t");

		while(true) {
			if(qel.next() == null) {
				DebugOut.println(qel.value());
				break;
			} else {
				DebugOut.print(qel.value() + ", ");
			}
			qel = qel.next();
		}

		// we still hold the reference to the currently printed queue at
		// this point!
		if (Config.getInt("NonStop", 0)==0) {
			EventService.waitEvent(Events.Wakeup);
			EventService.clearEvent(Events.Wakeup);
		}

		if (Config.getInt("UseGuards", 0)==1) {
			GC.guard(512,2);
		}
	}

	public void run() {
		QueueElement head, tail;

		head = tail = new QueueElement(runs++);

		while(true) {
			DebugOut.println("Queue Run " + runs);

			// remove first item from the list => garbage
			if(runs>Config.getInt("QueueLength", 4)) {
				if(tail == head) {
					tail = head.next();
				}
				head = head.next();
			}

			// append another element
			tail.next(new QueueElement(runs++));
			tail = tail.next();

			// print the queue and produce garbage
			if(Config.getInt("usePortal",0) == 1) {
				ListPrintService lps = (ListPrintService) PortalService.lookup("ListPrintService");
				lps.printList(head);
			} else {
				printList(head);
			}

			if (Config.getInt("UseGuards", 0)==1) {
				GC.guard(512,1);
			}

			if (Config.getInt("MaxRuns",0)!=0) {
				if (runs>=Config.getInt("MaxRuns",0)) {
					System.exit(0);
				}
			}
		}
	}
}
