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
package keso.coffeebreak;

import java.lang.annotation.NoHeapAllocation;
import keso.core.*;

/**
 * Class representing the free memory list of a domain.
 */
public class CoffeeListElement {
    CoffeeDomain dom;

    /**
     * Stores reference to domain, but does NOT initialize the list!
     * @param dom
     */
    @NoHeapAllocation
    public CoffeeListElement(CoffeeDomain dom) {
        this.dom = dom;
    }

    /**
     * @return the size in bytes of the underlying structure
     */
    @NoHeapAllocation
    public static int rawStructSize() {
        // weavelet
        return 0;
    }

    /**
     * Split the current element so that one object of the given size is allocated. The object is returned; the rest of
     * the free memory list element is enqueued instead of this element.
     * @param size size of the object to allocate in bytes
     * @param slotSize size of a slot in bytes
     * @return a raw, uninitialized object that was just allocated
     */
    @NoHeapAllocation
    public Object splitToObject(int size, int slotSize) {
        // weavelet
        return null;
    }

    /**
     * Return this whole list element as an object. Use, if the size of this element is too small for the object + one new
     * element. Use "splitToObject" else.
     * @return the current list elements memory as a raw, uninitialized object.
     */
    @NoHeapAllocation
    public Object elementAsObject() {
        // weavelet
        return null;
    }

    /**
     * Initialize the list to the currently set domain.
     */
    @NoHeapAllocation
    public void initListStart() {
        internalSetPrevPtr(dom.getHeapFreememAddress());
    }

    /**
     * Sets the internal list element pointer to the given value
     * @param address address the element pointer should point to
     */
    @NoHeapAllocation
    private void internalSetPrevPtr(int address) {
        // weavelet {
    }

    /**
     * Reset the domain's list to empty.
     */
    @NoHeapAllocation
    public void clearList() {
        initListStart();
    }

    /**
     * Append a new list element starting at a memory address with a give size in slots
     * @param startAddress start address where the new element should be placed
     * @param sizeInSlots size in slots of the new element
     */
    @NoHeapAllocation
    public void append(int startAddress, int sizeInSlots) {
        // weavelet
    }

    /**
     * Check if this list is at the last element. Any further next() calls will lead to an inconsistend state!
     * @return true if the current position is the last element, false if not.
     */
    @NoHeapAllocation
    public boolean atEnd() {
        // weavelet
        return true;
    }

    /**
     * Advance to the next element. Only valid, if not atEnd()
     */
    @NoHeapAllocation
    public void next() {
        // weavelet
    }

    /**
     * @return the size of the current element in slots
     */
    @NoHeapAllocation
    public int getSizeInSlots() {
        // weavelet
        return 0;
    }

    /**
     * Print size information about all list elements in their consecutive order.
     * ATTENTION: resets list to list start!
     */
    @NoHeapAllocation
    public void debugPrint() {
        for (initListStart(); !this.atEnd(); next()) {
            Marshal.printf("Size: %d slots\n", getSizeInSlots());
        }
    }

}
