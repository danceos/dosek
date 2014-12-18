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
 * The HookService provides constants and services for use
 * by HookRoutines, notably the ErrorHook.
 */
public final class HookService {
	/**
	 * The OSServiceId_<servicename> constants provide unique identifiers
	 * for each OSEK service. The ErrorHook may use the Service OSErrorGetServiceId
	 * to get the identifier of the system service where the error happened
	 *
	 * The values for these constants are taken from ProOSEK and may differ in
	 * other OSEK implementations.
	 */
	public static final int OSServiceId_ActivateTask = 3;
	public static final int OSServiceId_TerminateTask = 5;
	public static final int OSServiceId_ChainTask = 7;
	public static final int OSServiceId_GetTaskState = 9;
	public static final int OSServiceId_GetTaskID = 11;
	public static final int OSServiceId_Schedule = 13;
	public static final int OSServiceId_GetResource = 15;
	public static final int OSServiceId_ReleaseResource = 17;
	public static final int OSServiceId_SetEvent = 19;
	public static final int OSServiceId_ClearEvent = 21;
	public static final int OSServiceId_WaitEvent = 23;
	public static final int OSServiceId_GetEvent = 25;
	public static final int OSServiceId_GetAlarm = 27;
	public static final int OSServiceId_GetAlarmBase = 29;
	public static final int OSServiceId_SetRelAlarm = 31;
	public static final int OSServiceId_SetAbsAlarm = 33;
	public static final int OSServiceId_CancelAlarm = 35;
	public static final int OSServiceId_SuspendOSInterrupts = 37;
	public static final int OSServiceId_ResumeOSInterrupts = 39;
	public static final int OSServiceId_SuspendAllInterrupts = 41;
	public static final int OSServiceId_ResumeAllInterrupts = 43;
	public static final int OSServiceId_DisableAllInterrupts = 45;
	public static final int OSServiceId_EnableAllInterrupts = 47;
	public static final int OSServiceId_AdvanceCounter = 63;
	public static final int OSServiceId_IAdvanceCounter = 65;

	/**
	 * Provides the Service identifier of the service where an error has been
	 * risen
	 */
	public static int OSErrorGetServiceId() { return 0; }

	/**
	 * Allows access to parameters of the system service which called ErrorHook.
	 * This variant is to query any integer parameters.
	 * The use of the correct variant is the users duty, in case the wrong variant
	 * is used the generated code will not compile.
	 *
	 * Valid values for systemServiceName is the name of the method in the KESO
	 * interface, not the name of the corresponding OSEK call. Likewise the
	 * parameter names are the ones defined in the KESO interface, not the
	 * OSEK interface.
	 */
	public static int OSError_int(String systemServiceName, String paramName) {
		return 0;
	}

	/**
	 * Allows access to parameters of the system service which called ErrorHook.
	 * This variant is to query any Object derived parameters.
	 * The use of the correct variant is the users duty, in case the wrong variant
	 * is used the generated code will not compile.
	 *
	 * Valid values for systemServiceName is the name of the method in the KESO
	 * interface, not the name of the corresponding OSEK call. Likewise the
	 * parameter names are the ones defined in the KESO interface, not the
	 * OSEK interface.
	 */
	public static Object OSError_obj(String systemServiceName, String paramName) {
		return null;
	}
}
