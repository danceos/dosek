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

import java.lang.annotation.NoHeapAllocation;

/**
 * Class containing the allocator of the java based CoffeeBreak implementation.
 */
public class CoffeeBreakAllocator {
    private CoffeeBreakAllocator() {
        // static methods only
    }

    /**
     * Allocate an object of the type specified by the classId on the heap. Throws an error if heap memory has
     * been exhausted.
     * @param classId class id of the object
     * @param bytesize size of the object on the heap
     * @param roff used for the object header
     * @return the allocated object
     */
    @NoHeapAllocation
    public static Object coffeeBreakAlloc(int classId, int bytesize, int roff) {
        Object retVal;
        Object rawObj;

        CoffeeDomain currDomain = new CoffeeDomain();
        CoffeeListElement elem = new CoffeeListElement(currDomain);
        int size;

        size = bytes2slot(bytesize, currDomain.getSlotSize());

        GCUtils.lock();

        for (elem.initListStart(); !elem.atEnd(); elem.next()) {
            if (elem.getSizeInSlots() >= size) {
                break;
            }
        }

        if (elem.atEnd()) {
            GCUtils.unlock();
            Marshal.error("JavaCoffeeBreak: out of memory\n");
        }

        // default: KESO_HEAP_HAS_TINY_SLOTS behavior
        if (elem.getSizeInSlots() > size
                && (elem.getSizeInSlots() - size) * currDomain.getSlotSize() >= CoffeeListElement.rawStructSize()) {
            // split block
            rawObj = elem.splitToObject(size, currDomain.getSlotSize());
        } else {
            Marshal.printf("using block as object\n");
            rawObj = elem.elementAsObject();
        }

        Marshal.zeroMemory(rawObj, size * currDomain.getSlotSize());

        retVal = currDomain.setClassId(rawObj, classId, roff);
        currDomain.colorObject(retVal);

        currDomain.setSasls(currDomain.getSasls() + size * currDomain.getSlotSize());
        currDomain.setHeapFree(currDomain.getHeapFree() - size * currDomain.getSlotSize());

        GCUtils.unlock();

        return retVal;
    }

    /**
     * Convert a size given in bytes to the size in slots.
     * @param bytesize size to convert
     * @param slotSize size of one slot in bytes.
     * @return the number of slots an object of size size will take.
     */
    @NoHeapAllocation
    private static int bytes2slot(int bytesize, int slotSize) {
        return (slotSize - 1 + bytesize) / slotSize;
    }
}