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

package keso.core;

public abstract class TaskService {

	public static final int E_OK          = 0;
	public static final int E_OS_ACCESS   = 1;
	public static final int E_OS_CALLEVEL = 2;
	public static final int E_OS_ID       = 3;
	public static final int E_OS_LIMIT    = 4;
	public static final int E_OS_NOFUNC   = 5;
	public static final int E_OS_RESOURCE = 6;
	public static final int E_OS_STATE    = 7;
	public static final int E_OS_VALUE    = 8;

	/* 						STANDARD OSEK API */
	/**
	 * The task <taskID> is transferred from the suspended state into the ready state.
	 * The operating system ensures that the task code is being executed from the first
	 * statement. ActivateTask will not immediately change the state of the task in case
	 * of multiple activation requests. If the task is not suspended, the activation will
	 * only be recorded and performed later.
 	 *
	 * @return
	 *     Standard: No error (E_OK), Too many task activations of <taskID> (E_OS_LIMIT)
	 *     Extended: Task <TaskID> is invalid (E_OS_ID)
	 */
	public static int activate(Thread taskID) { return E_OK; }

	/**
	 * This service causes the termination of the calling task. The calling task is
	 * transferred from the running state into the suspended state. In case of tasks
	 * with multiple activation requests, terminating the current instance of the
	 * task automatically puts the next instance of the same task into ready state.
	 *
	 * @return
	 *     Standard: No return to call level
	 *     Extended: Task still occupies resources (E_OS_RESOURCE)
	 *	        Call at interrupt level (E_OS_CALLEVEL)
	 */
	public static int terminate() { return E_OK; }

	/**
	 * This service causes the termination of the calling task. After termination of
	 * the calling task a succeeding task <TaskID> is activated. Using this service,
	 * it ensures that the succeeding task starts to run at the earliest after the
	 * calling task has been terminated.
	 *
	 * @return
	 *     Standard: No return to call level
	 *               To many task activations of <TaskID> (E_OS_LIMIT)
	 *     Extended: Task <TaskID> is invalid (E_OS_ID)
	 * 		 Calling task still occupies resoureces (E_OS_RESOURCE)
	 *		 Call at interrupt level (E_OS_CALLEVEL)
	 */
	public static int chain(Thread taskID) { return E_OK; }

	/**
	 * If a higher-priority task is ready, the internal resource of the task is released,
	 * the current task is put into the ready state, its context is saved and the
	 * higher-priority task is executed. Otherwise the calling task is continued.
	 */
	public static void schedule() {}

	/**
	 * GetTaskID returns the information about the TaskID of the task which is currently
	 * running.
	 *
	 * The service may be called from interrupt service routines, task level, and some
	 * hook routines. When a call is made from a task in a full
	 * preemptive system, the result may already be incorrect at the time of evaluation.
	 * When the service is called for a task, which is activated more than once, the
	 * state is set to running if any instance of the task is running.
	 */
	public static Thread getTaskID() { return null; }

	/**
	 * Returns the state of a task (running, ready, waiting, suspended) at the time of calling
	 * GetTaskState.
	 *
	 * The service may be called from interrupt service routines, task level, and some
	 * hook routines. When a call is made from a task in a full preemptive system,
	 * the result may already be incorrect at the time of evaluation. When the
	 * service is called for a task, which is activated more than once, the state
	 * is set to running if any instance of the task is running.
	 */
	public static int getTaskState(Thread taskID) {
			return -1;
	}

	/* 						KESO EXTENSIONS */

	/**
	 * Fetch the Task object of another Task determined by its name.
	 * Only Tasks within the current tasks domain can be found.
	 *
	 * A specific task will have assigned the same task object over
	 * the entire runtime of the system, so one might want to cache
	 * the result of a Task lookup to avoid unneccesary calls where
	 * possible.
	 *
	 * @param  taskName Name of the task as specified in keso configuration.
	 * 	This must be a constant string, since it will be resolved
	 * 	at compile time.
	 * @return null if a task with the provided name cannot be found within the
	 * 	domain. Otherwise a reference to the object of the found task is returned.
	 */
	public static Thread getTaskByName(String taskName) { return null; }
}
