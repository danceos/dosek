// @formatter:off
/**(c)

 Copyright (C) 2006-2015 Christian Wawersich, Michael Stilkerich,
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
package keso.coffeebreak;

import java.lang.annotation.NoHeapAllocation;

/**
 * Provides access to generic GC functions.
 */
public class GCUtils {
    /**
     * Lock the garbage collector.
     */
    @NoHeapAllocation
    public static void lock() {
        // weavelet
    }

    /**
     * Unlock the garbage collector.
     */
    @NoHeapAllocation
    public static void unlock() {
        // weavelet
    }

    /**
     * TODO: this should really be a domain property - only works for 1 domain
     * Get the system's root set size.
     * @return size of the root set array
     */
    @NoHeapAllocation
    public static int getRootSetSize() {
        // weavelet
        return 0;
    }
}
