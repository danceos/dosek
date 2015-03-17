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

public class CoffeeBlocking {

    private CoffeeBlocking() {
    }

    /**
     * @return the number of blocking tasks in the system
     */
    @NoHeapAllocation
    public static int getNumBlockingTasks() {
        // weavelet
        return 0;
    }

    /**
     * Set the internal stack pointer of the passed CoffeeTaskStack to the stack of the
     * blocking task with the given index.
     * @param index index into the blocking task array
     * @param stack the stack whose internal stack pointer should be modified
     * @return the instance of a CoffeeTaskStack that was passed as parameter
     */
    @NoHeapAllocation
    public static CoffeeTaskStack getStackByTask(int index, CoffeeTaskStack stack) {
        // weavelet
        return null;
    }
}
