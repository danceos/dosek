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
 * Provides access to Counter/Alarm related OSEK system services.
 */
public final class AlarmService {
	/**
	 * Read the AlarmBase characteristics of an Alarm.
	 *
	 * The characteristics of the Alarm will be written to info,
	 * an object of class AlarmBase provided by the caller.
	 *
	 * @param alarmID Alarm system object the base of which is to be determined.
	 * @param info    output AlarmBase object where the attributes of the underlying
	 *                       counter will be stored in.
	 * @return return value of the underlying OSEK call
	 */
	public static int getAlarmBase(Alarm alarmID, AlarmBase info) { return 0; }

	/**
	 * Query relative value in ticks before the Alarm expires.
	 *
	 * TODO return status is not accessable by the application. Throw
	 * an OSEKException when an error occurs.
	 *
	 * @param  alarmID Alarm system object of the alarm to be queried
	 * @return number of counter ticks till the alarm expires
	 */
	public static int getAlarm(Alarm alarmID) { return 0; }

	/**
	 * Winds up the Alarm specified by alarmID relative to the current counter value.
	 * After increment ticks have elapsed the task assigned to this alarm is
	 * activated/the assigned event is set/the alarm callback routine is called.
	 *
	 * @param alarmID   Alarm system object of the alarm to be configured
	 * @param increment number of counter (major) ticks relative to the current
	 *                  counter value until the alarm triggers
	 * @param cycle     number of counter (major) ticks that a cyclic alarm is
	 *                  triggered with. Becomes active after the first shot
	 *                  configured by increment was triggered. Use 0 for a
	 *                  single-shot alarm.
	 * @return return value of the underlying OSEK call
	 */
	public static int setRelAlarm(Alarm alarmID, int increment, int cycle) { return 0; }

	/**
	 * Winds up the Alarm specified by alarmID using an absolute counter value.
	 * After start ticks are reached by the base counter the task assigned to
	 * this alarm is activated/the assigned event is set/the alarm callback
	 * routine is called.
	 *
	 * @param alarmID   Alarm system object of the alarm to be configured
	 * @param start     absolute counter (major) tick value at which the alarm
	 *                  triggers
	 * @param cycle     number of counter (major) ticks that a cyclic alarm is
	 *                  triggered with. Becomes active after the first shot
	 *                  configured by increment was triggered. Use 0 for a
	 *                  single-shot alarm.
	 * @return return value of the underlying OSEK call
	 */
	public static int setAbsAlarm(Alarm alarmID, int start, int cycle) { return 0; }

	/**
	 * Cancels the Alarm specified by alarmID.
	 *
	 * @param alarmID Alarm system object of the alarm to be configured
	 * @return return value of the underlying OSEK call
	 */
	public static int cancelAlarm(Alarm alarmID) { return 0; }

	/* KESO extensions */

	/**
	 * Get a reference to an Alarm object by specifying its name as it was
	 * defined in KESORC.
	 *
	 * @param  name Name of the alarm whose system object should be returned.
	 *              Must be a String constant.
	 * @return To enforce service protection, the system object will only be
	 *         provided if the queried alarm either belongs to the calling domain
	 *         or if it was explicitely made available to the calling domain
	 *         using the ImportAlarm directive in the KESORC file. Otherwise this
	 *         service returns null. If no alarm with the given name exists, this
	 *         service returns null as well.
	 */
	public static Alarm getAlarmByName(String name) {	return null; }

}
