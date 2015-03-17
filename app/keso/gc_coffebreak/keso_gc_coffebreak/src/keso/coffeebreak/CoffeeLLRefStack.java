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
 * Class that stores a stack composed of references. Used for accessing the linked list of references to scan the
 * stacks of currently blocked tasks in the CoffeeBreak garbage collector.
 */
public class CoffeeLLRefStack {
    public CoffeeLLRefStack() {
    }

    /**
     * Advance to the next object in the current stack frame.
     */
    @NoHeapAllocation
    public void nextObject() {
        // weavelet
    }

    /**
     * Advance to the next frame on the stack.
     */
    @NoHeapAllocation
    public void nextFrame() {
        // weavelet
    }

    /**
     * Check if this stack has is at the last element (only checks for end, not if an entry is object or stack reference).
     * @return true if this is the end of the stack, else false.
     */
    @NoHeapAllocation
    public boolean atEnd() {
        // weavelet
        return false;
    }

    /**
     * @return true if this stack is empty, else false.
     */
    @NoHeapAllocation
    public boolean isEmptyStack() {
        // weavelet
        return false;
    }

    /**
     * Get the current object.
     * @return the current object in the iteration.
     */
    @NoHeapAllocation
    public Object currentObject() {
        // weavelet
        return null;
    }

    /**
     * Check if an entry is a stack reference. Use nextFrame() to advance to the next frame if so.
     * @return true if the current entry is a stack reference.
     */
    @NoHeapAllocation
    public boolean isStackRef() {
        // weavelet
        return false;
    }
}
