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

public final class Domain_RDS {
    private Domain_RDS() {
    }

    /**
     * Sets the address value of the pointer to the new ptr domain attribute
     * @param ptr
     */
    @NoHeapAllocation
    public static void setHDNewPtr(IntPtr ptr) {
        ptr.setAddress(getNewPtrValue());
    }

    /**
     * Sets the address value of the pointer to the heap end domain attribute
     * @param ptr
     */
    @NoHeapAllocation
    public static void setHDHeapEnd(IntPtr ptr) {
        ptr.setAddress(getHeapEndValue());
    }

    /**
     * Subtract a size value from the heap free property of the domain
     * @param i size in bytes to subtract
     */
    @NoHeapAllocation
    public static void subHeapFree(int i) {
        // weavelet
    }

    /**
     * Get a memory chunk of the specified size from the heap of this domain. Does not initialize class id and roff!
     * @param size size of the object structure
     * @return a raw (uninitialized) object
     */
    @NoHeapAllocation
    public static Object allocateRawObject(int size) {
        return null;
    }

    /**
     * Set class id and roff for a given raw object, converting it to a "real" object.
     * @param object uninitialized object structure to convert
     * @param class_id the class id to set
     * @param roff the roff
     * @return a properly initialized object ready for use
     */
    @NoHeapAllocation
    public static Object setClassId(Object object, int class_id, int roff) {
        return null;
    }

    /**
     * @return the integer value of the "new" address of this domain
     */
    @NoHeapAllocation
    private static int getNewPtrValue() {
        // weavelet
        return 0;
    }

    /**
     * @return the integer value of the "heap end" address of this domain
     */
    @NoHeapAllocation
    private static int getHeapEndValue() {
        // weavelet
        return 0;
    }
}
