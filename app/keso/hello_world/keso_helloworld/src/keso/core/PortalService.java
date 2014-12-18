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
 * This class provides the global name service for the inter-domain-communication.
 */
public final class PortalService {

	/**
	 * Returns a proxy object for the remote service.
	 *
	 * The service import must be described in the KESORC file. If the calling
	 * domain is not allowed to access the service, this function will return
	 * a null reference.
	 */
	public static Portal lookup(String name) { return null; }

	/**
	 * Returns the domain local service object.
	 *
	 * The service must be described in the KESORC file and is created on domain startup.
	 * If the calling domain is not the domain exporting the named service, this function
	 * will return a null reference.
	 */
	public static Service getService(String name) { return null; }

	/**
	 * call the packet handler of a remote service
	 */
	public static void handlePackets(String service, String network) {}

}
