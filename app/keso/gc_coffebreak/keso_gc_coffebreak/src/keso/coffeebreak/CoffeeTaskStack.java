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
 * Class representing a list of stack partitions of a blocking task.
 */
public class CoffeeTaskStack {
    @NoHeapAllocation
    public CoffeeTaskStack() {
    }

    /**
     * Advance to the next stack partition.
     */
    @NoHeapAllocation
    public void next() {
        // weavelet
    }

    /**
     * Check if the iteration is at end. Do not access further elements if so!
     * @return true if the iteration has ended, false if the current element is valid.
     */
    @NoHeapAllocation
    public boolean atEnd() {
        // weavelet
        return false;
    }

    /**
     * Store the pointer to the llref list of the current stack partition in the object given as parameter.
     * @param llRefStack a CoffeeLLRefStack object whose internal llref pointer should be set.
     * @return the object passed as parameter
     */
    @NoHeapAllocation
    public CoffeeLLRefStack getLLRefs(CoffeeLLRefStack llRefStack) {
        // weavelet
        return llRefStack;
    }

    /**
     * Check if the current partition belongs to the CoffeeDomain currently undergoing garbage collection.
     * @param dom domain currently being examined
     * @return true if domain matches, false if not.
     */
    @NoHeapAllocation
    public boolean checkDomain(CoffeeDomain dom) {
        // weavelet
        return false;
    }
}
