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

// for Marshal and IntPtr class
import keso.core.*;

import java.lang.annotation.NoHeapAllocation;

/**
 * Class representing a domain structure for CoffeeBreak domains. See the corresponding kni/CoffeeDomain class for the
 * weavelet implementation.
 */
public class CoffeeDomain {
    /**
     * Initialize this instance with the current domain. Not valid outside of domain context!
     */
    @NoHeapAllocation
    public CoffeeDomain() {
        // weavelet
    }

    /**
     * Initialize the domain representation using a specified domain id. Useful in code operating outside of the traditional
     * domain model, e.g. the garbage collector.
     * @param domainId the domain of the domain this object should represent
     */
    @NoHeapAllocation
    public CoffeeDomain(int domainId) {
        // weavelet
    }

    /**
     * @return the size of a slot in bytes
     */
    @NoHeapAllocation
    public int getSlotSize() {
        // weavelet
        return 0;
    }

    /**
     * Get the SASL field of the domain structure.
     * @return the number of Slots Allocated Since Last Scan
     */
    @NoHeapAllocation
    public int getSasls() {
        // weavelet
        return 0;
    }

    /**
     * Set the Slots Allocated Since Last Scan field of the domain.
     * @param value value to set
     */
    @NoHeapAllocation
    public void setSasls(int value) {
        // weavelet
    }

    /**
     * @return number of free bytes in the heap
     */
    @NoHeapAllocation
    public int getHeapFree() {
        // weavelet
        return 0;
    }

    /**
     * Set the number of bytes free on the heap of the domain to a new value.
     * @param value value to set
     */
    @NoHeapAllocation
    public void setHeapFree(int value) {
        // weavelet
    }

    /**
     * Calculates the size of the heap of this domain.
     * @return size of the heap in bytes
     */
    @NoHeapAllocation
    public int getHeapSize() {
        // weavelet
        return 0;
    }

    /**
     * Get the top of the heap from the domain.
     * @return address of the top of the heap
     */
    @NoHeapAllocation
    public int getHeapBegin() {
        // weavelet
        return 0;
    }

    /**
     * The freemem field of the domain stores the start element of the free memory list.
     * @return the address of the freemem field of the domain.
     */
    @NoHeapAllocation
    public int getHeapFreememAddress() {
        // weavelet
        return 0;
    }

    /**
     * Given a raw object pointer (pointing to the address of an uninitialized object), equip this object with its class id
     * and add the correct offset to the object address to enable storing its fields.
     * @param obj pointer to a previously uninitialized object that was retrieved within the allocation method.
     * @param class_id system-wide class id to set
     * @param roff offset to enable the object fields
     * @return
     */
    @NoHeapAllocation
    public Object setClassId(Object obj, int class_id, int roff) {
        // weavelet
        return null;
    }

    /**
     * Color the color bit of the passed object with the color currently associated with this domain.
     * @param obj object to color
     */
    @NoHeapAllocation
    public void colorObject(Object obj) {
        // weavelet
    }

    /**
     * Check if this object is colored in the currently set color of this domain.
     * @param obj object to check
     * @return true if this object is colored in the color of the color bit of this domain, false if not
     */
    @NoHeapAllocation
    public boolean isObjectColored(Object obj) {
        // weavelet
        return false;
    }

    /**
     * Toggle the color bit of this domain.
     */
    @NoHeapAllocation
    public void toggleColorBit() {
        // weavelet
    }

    /**
     * From the root set array of persistent objects in this domain, retrieve the object stored at a given offset.
     * Attention: Boundary checks are currently not performed!
     * @param index offset into the root set array.
     * @return an object pointer to a root object.
     */
    @NoHeapAllocation
    public Object rootObjectAt(int index) {
        // weavelet
        return null;
    }

    /**
     * Get the number of references stored in this object.
     * @param o object to get the reference count from.
     * @return Positive number if references available and the system uses object arrays for references; negative number
     * if references available and stored using "roff" mechanism; in both cases zero if no reference available.
     */
     @NoHeapAllocation
     public int refCount(Object o) {
         // weavelet
         return 42;
     }

    /**
     * Get a reference stored in an object at offset index.
     * @param o object whose references should be accessed
     * @param index may be positive if object arrays are used for references; negative if "roff" mechanism is used
     * @return the object reference
     */
    @NoHeapAllocation
    public Object getReference(Object o, int index) {
        // weavelet
        return new Object();
    }

    /**
     * Check if an object is on the heap of this domain.
     * @param o the object to check
     * @return true if the object is on the heap of this domain; false if not.
     */
    @NoHeapAllocation
    public boolean isOnHeap(Object o) {
        // weavelet
        return false;
    }

    /**
     * Return the size of an object in slots for this domain
     * @param o object to get size for
     * @return size in slots of the object
     */
    @NoHeapAllocation
    public int getObjectSize(Object o) {
        // TODO check if keso_ObjSize may be implemented in Java
        int size = internalSize(this.getSlotSize(), o);
        return size;
    }

    /**
     * Internal stub redirected to KESO's keso_objSize implementation
     * @param slotSize size of a slot in byte
     * @param o  object to get size for
     * @return size in slots of the object
     */
    @NoHeapAllocation
    private int internalSize(int slotSize, Object o) {
        // weavelet
        return 0;
    }
}
