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

import keso.core.TaskService;
import keso.core.Task;

public final class Thread implements Runnable,keso.core.NonCopyable {
	/** The maximum priority that a thread can have. */
	public static final int MAX_PRIORITY=1;
	/** The minimum priority that a thread can have. */
	public static final int MIN_PRIORITY=0;
	/** The default priority that is assigned to a thread. */
	public static final int NORM_PRIORITY=1;

	//private Runnable user_object;
	private String name;
	private int prio;

	private Thread() { }
	private Thread(Runnable target) { }
	private Thread(String name) { this.name = name; }

	public static int activeCount() {
		return 0;
	}

	public static Thread currentThread() {
		return TaskService.getTaskID();
	}

	public String getName() {
		return name;
	}

	public int getPriority() {
		return prio;
	}

	public void interrupt() {
		throw new Error("not implemented");
	}

	public boolean isAlive() {
		return (TaskService.getTaskState(this) != Task.suspendedState());
	}

	public void join() {
		throw new Error("not implemented");
	}

	// XXX issue with portals: the run method may access the reference of the
	// runnable or other references stored therein in a service domain
	public void run() {
//		if(user_object != null) {
//			user_object.run();
//		}
	}

	public void setPriority(int newPriority) {
		throw new Error("not implemented");
	}

	public static void sleep(long millis) {
		throw new Error("not implemented");
	}

	public void start() {
		TaskService.activate(this);
	}

	public String toString() {
		return ("Task " + getName() + " (Priority " + getPriority() + ")");
	}

	public static void yield() {
		TaskService.schedule();
	}

	public void setDaemon(boolean setting) {
		throw new Error("not implemented");
	}
}
