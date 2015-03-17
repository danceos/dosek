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
 * Working stack for the Java based CoffeeBreak implementation.
 */
public class CoffeeStack {
    @NoHeapAllocation
    private CoffeeStack() {
    }

    /**
     * Push an object to the stack.
     * @param o object to push.
     */
    @NoHeapAllocation
    public static void push(Object o) {
        // weavelet
    }

    /**
     * Pop an object from the stack. Uses KESO_THROW_ERROR if the stack is empty.
     * @return object from the stack
     */
    @NoHeapAllocation
    public static Object pop() {
        // weavelet
        return null;
    }

    /**
     * Check if the stack is empty.
     * @return true if the stack is empty, else false.
     */
    @NoHeapAllocation
    public static boolean isEmpty() {
        // weavelet
        return false;
    }
}
