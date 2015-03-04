// @formatter:off
/**(c)

 Copyright (C) 2006-2014 Christian Wawersich, Michael Stilkerich,
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

import java.lang.annotation.NoHeapAllocation;

/**
 * The Marshal class provides methods to access low-level functionality from a Java application.
 */
public final class Marshal {
    private Marshal() {
        // for static access only
    }

    /**
     * Wrapper to call KESO_PRINTF from Java code.
     * @param message message string to print
     */
    @NoHeapAllocation
    public static void printf(String message) {
        // Weavelet
    }

    /**
     * Wrapper for KESO_THROW_ERROR to terminate the system in case of an error.
     * @param message message string to print
     */
    @NoHeapAllocation
    public static void error(String message) {
        // Weavelet
    }

    /**
     * Overwrite memory of an uninitialized object with zeros
     * @param target object to overwrite
     * @param size size of the memory in bytes
     */
    @NoHeapAllocation
    public static void zeroMemory(Object target, int size) {
        // Weavelet
    }
}
