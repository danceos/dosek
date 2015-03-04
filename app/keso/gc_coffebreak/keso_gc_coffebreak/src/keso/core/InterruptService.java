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
 * Provides access to interrupt-handling related OSEK system services.
 */
public final class InterruptService {

	/**
	 * This service disables all interrupts for which the hardware supports
	 * disabling. The state before is saved for the enableAll() call.
	 *
	 * The service may be called from an ISR category 1 and category 2 and
	 * from the task level, but not from hook routines. This service is
	 * intended to start a critical section of the code. This section shall
	 * be finished by calling the EnableAllInterrupts service.
	 * No API service calls are allowed within this critical section. The
	 * implementation should adapt this service to the target hardware
	 * providing a minimum overhead. Usually, this service disables recognition
	 * of interrupts by the central processing unit. Note that this service
	 * does not support nesting. If nesting is needed for critical sections
	 * e.g. for libraries suspendOS/resumeOS or suspendAll/resumeAll should be used.
	 *
	 * Status:
	 *     Standard: none
	 *     Extended: none
	 */
	public static void disableAll() {};

	/**
	 * This service restores the state saved by DisableAllInterrupts.
	 *
	 * The service may be called from an ISR category 1 and category 2
	 * and from the task level, but not from hook routines. This service
	 * is a counterpart of disableAll service, which has to be called
	 * before, and its aim is the completion of the critical section
	 * of code. No API service calls are allowed The implementation should
	 * adapt this service to the target hardware providing a minimum overhead.
	 * Usually, this service enables recognition of interrupts by the
	 * central processing unit.
	 *
	 * Status:
	 *     Standard: none
	 *     Extended: none
	 */
	public static void enableAll() {};

	/**
	 * This service saves the recognition status of all interrupts and disables
	 * all interrupts for which the hardware supports disabling.
	 *
	 * The service may be called from an ISR category 1 and category 2, from
	 * alarm-callbacks and from the task level, but not from all hook routines.
	 * This service is intended to protect a critical section of code from
	 * interruptions of any kind. This section shall be finished by calling the
	 * resumeAll service.
	 * No API service calls beside suspendAll/resumeAll pairs and suspendOS/resumeOS
	 * pairs are allowed within this critical section.
	 *
	 * The implementation should adapt this service to the target hardware providing
	 * a minimum overhead.
	 *
	 * Status:
	 *     Standard: none
	 *     Extended: none
	 */
	public static void suspendAll() {};

	/**
	 * This service restores the recognition status of all interrupts saved by
	 * the suspendAll service.
	 *
	 * The service may be called from an ISR category 1 and category 2, from
	 * alarm-callbacks and from the task level, but not from all hook routines.
	 * This service is the counterpart of suspendAll service, which has
	 * to have been called before, and its aim is the completion of the critical
	 * section of code. No API service calls beside suspendAll/resumeAll pairs
	 * and suspendOS/resumeOS pairs are allowed within this critical section.
	 *
	 * Status:
	 *     Standard: none
	 *     Extended: none
	 */
	public static void resumeAll() {};

	/**
	 * This service saves the recognition status of interrupts of category 2
	 * and disables the recognition of these interrupts.
	 *
	 * The service may be called from an ISR and from the task level, This
	 * service is intended to protect a critical section of code. This section
	 * shall be finished by calling the resumeOS service. No API
	 * service calls beside suspendAll/resumeAll pairs and suspendOS/resumeOS
	 * pairs are allowed within this critical section.
	 *
	 * The implementation should adapt this service to the target hardware
	 * providing a minimum overhead. It is intended only to disable interrupts
	 * of category 2. However, if this is not possible in an efficient way
	 * more interrupts may be disabled.
	 *
	 * Status:
	 *     Standard: none
	 *     Extended: none
	 */
	public static void suspendOS() {};

	/**
	 * This service restores the recognition status of interrupts saved by the
	 * suspendOS service.
	 *
	 * The service may be called from an ISR category 1 and category 2 and from
	 * the task level, but not from hook routines. This service is the counterpart
	 * of suspendOS service, which has to have been called before, and its aim
	 * is the completion of the critical section of code. No API service calls
	 * beside suspendAll/resumeAll pairs and suspendOS/resumeOS pairs are allowed
	 * within this critical section. The implementation should adapt this service
	 * to the target hardware providing a minimum overhead. suspendOS/resumeOS
	 * can be nested. In case of nesting pairs of the calls suspendOS and resumeOS
	 * the interrupt recognition status saved by the first call of suspendOS
	 * is restored by the last call of the resumeOS service.
	 *
	 * Status:
	 *     Standard: none
	 *     Extended: none
	 */
	public static void resumeOS() {};

	/**
	 * Provides the IRQ level (priority) of an ISR.
	 *
	 * @param  isrName name (string constant) of the ISR as defined in KESORC.
	 * @return The IRQ level (priority) of that ISR.
	 */
	public static int getIRQLevel(String isrName) { return -1; };
}

