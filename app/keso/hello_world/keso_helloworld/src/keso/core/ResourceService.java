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

/**
 * Provides access to Resource related OSEK system services.
 */
public final class ResourceService {

	/**
	 * This call serves to enter critical sections in the code that are assigned
	 * to the resource referenced by ResID. A critical section shall always
	 * be left using ReleaseResource.
	 *
	 * Nested resource occupation is only allowed if the inner critical sections
	 * are completely executed within the surrounding critical section (strictly stacked).
	 * Nested occupation of one and the same resource is also forbidden! It is
	 * recommended that corresponding calls to getResource and releaseResource
	 * appear within the same method or class.
	 * It is not allowed to use services which are points of rescheduling for non
	 * preemptable tasks (terminateTask,chainTask, schedule and waitEvent) in critical
	 * sections. Additionally, critical sections are to be left before completion of
	 * an interrupt service routine. Generally speaking, critical sections should be short.
	 * The service may be called from an ISR and from task level.
	 * Status
	 *     Standard: No error (E_OK)
	 *     Extended: Resource ResID is invalid (E_OS_ID)
	 *		 Attempt to get a resource which is already occupied by any task or ISR,
	 *	 	 or the statically assigned priority of the calling task or interrupt
	 * 		 routine is higher than the calculated ceiling priority (E_OS_ACCESS)
	 *
	 * @param resource Resource system object of the resource to be occupied.
	 * @return OSEK status
	 */
	public static int getResource(Resource resource) { return 0; }

	/**
	 * releaseResource is the counterpart of getResource and serves to leave critical
	 * sections in the code that are assigned to the resource referenced by ResID.
	 * For information on nesting conditions, see {@link #getResource(Resource)}.
	 * Status:
	 *     Standard: No error (E_OK)
	 *     Extended: Resource ResID is invalid (E_OS_ID)
	 *		 Attempt to get a resource which is already occupied by any task or ISR,
	 *	 	 or the statically assigned priority of the calling task or interrupt
	 * 		 routine is higher than the calculated ceiling priority (E_OS_ACCESS)
	 *
	 * @param resource Resource system object of the occupied resource to be released.
	 * @return OSEK status
	 */
	public static int releaseResource(Resource resource) { return 0; }

	/*					KESO extensions */

	/**
	 * Get a reference to a Resource object by specifying its name as it was
	 * defined in KESORC.
	 *
	 * The special name RES_SCHEDULER may be used to get a reference to the
	 * Scheduler resource, but only if USERESSCHEDULER was set to true in kesorc.
	 *
	 * @param  name Name of the resource whose system object should be returned.
	 *              Must be a String constant.
	 * @return To enforce service protection, the system object will only be
	 *         provided if the queried resource either belongs to the calling domain
	 *         or if it was explicitely made available to the calling domain
	 *         using the ImportResource directive in the KESORC file. Otherwise this
	 *         service returns null. If no resource with the given name exists, this
	 *         service returns null as well.
	 */
	public static Resource getResourceByName(String name) {	return null; }

	/**
	 * Occupy the special Scheduler Resource.
	 * The OSEK scheduler Resource is not occupied using the regular
	 * getResource() service. Instead, this method is used.
	 */
	public static int getScheduler() { return 0; }

	/**
	 * Release the special Scheduler Resource.
	 * The OSEK scheduler Resource is not released using the regular
	 * releaseResource() service. Instead, this method is used.
	 */
	public static int releaseScheduler() { return 0; }
}
