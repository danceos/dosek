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

import keso.core.*;
import keso.coffeebreak.*;
import keso.io.*;

import java.lang.annotation.NoHeapAllocation;

/**
 * Main class for the Java CoffeeBreak implementation providing stubs.
 */
public class JavaCoffeeBreak {
    private JavaCoffeeBreak() {
    }

    /**
     * Stub for allocation method
     * @param class_id
     * @param bytesize
     * @param roff
     * @return
     */
    @NoHeapAllocation
    public static Object keso_coffee_break_alloc(int class_id, int bytesize, int roff) {
        return CoffeeBreakAllocator.coffeeBreakAlloc(class_id, bytesize, roff);
    }

    /**
     * Stub for the main method performing mark and sweep
     * @param did domain id of the domain to be garbage collected
     * @return 1 if collection was executed, 0 if not
     */
    @NoHeapAllocation
    public static int coffee_break_main(int did) {
        return CoffeeBreakCollector.JavaCoffeeBreakMain(did);
    }
}
