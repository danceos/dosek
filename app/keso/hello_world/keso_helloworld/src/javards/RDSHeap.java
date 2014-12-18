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
package javards;

import keso.core.*;
import keso.io.*;
import java.lang.annotation.*;

/**
 * Heap implementation of the restricted domain scope heap (see template rds-alloc.c) in Java.
 */
public class RDSHeap {
    private RDSHeap()
    {
    }

    @NoHeapAllocation
    public static Object keso_rds_alloc(int class_id, int size, int roff)
    {
        IntPtr newPtr = new IntPtr();
        IntPtr heapEnd = new IntPtr();

        int sizeAligned = alignObject(size);

        Object rawObj = Domain_RDS.allocateRawObject(sizeAligned);

        Domain_RDS.setHDNewPtr(newPtr);
        Domain_RDS.setHDHeapEnd(heapEnd);

        if(newPtr.compareTo(heapEnd) > 0) {
            Marshal.error("Error: Heap size limit reached!\n");
        }

        Domain_RDS.subHeapFree(sizeAligned);

        Marshal.zeroMemory(rawObj, sizeAligned);

        Object retVal = Domain_RDS.setClassId(rawObj, class_id, roff);

        return retVal;
    }

    @NoHeapAllocation
    static int alignObject(int size)
    {
        return (size + 3) &~3;
    }
}
