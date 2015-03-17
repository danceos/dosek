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
import keso.core.*;

/**
 * Java representation of the bitmap used in the CoffeeBreak garbage collector. Provides access methods and has its own
 * bitmap array. Consult the kni/CoffeeBitmap class for more information about its internal implementation.
 */
public final class CoffeeBitmap {
    private CoffeeBitmap() {
        // static class
    }

    /**
     * Mark all slots that are occupied by the object in the given domain as used.
     * @param dom the domain providing the heap the object resides on.
     * @param o the object that uses heap memory
     * @return the number of marked slots
     */
    @NoHeapAllocation
    public static int markObject(CoffeeDomain dom, Object o) {
        if (dom.isOnHeap(o))  {
            int sizeInSlots = dom.getObjectSize(o);
            int firstSlot = addr2Slot(dom, o);

            // Marshal.printf("Marking object starting at %d with size %d slots\n", firstSlot, sizeInSlots);
            markSlots(firstSlot, sizeInSlots);
            return sizeInSlots;
        }
        return 0;
    }

    /**
     * Find at max maxSlots consecutive free slots starting at startSlot (included)
     * @param startSlot the slot to start searching at
     * @param maxSlots maximum number of slots to search
     * @return size of the free block that was found in slots or zero if no block was found
     */
    @NoHeapAllocation
    public static int findFreeBlock(int startSlot, int maxSlots) {
        int blockStart;
        int blockEnd;

        if (maxSlots == 0) {
            return 0;
        }

        blockStart = findBit(startSlot, maxSlots, 0);
        maxSlots -= blockStart - startSlot;

        if (maxSlots == 0) {
            // no free block in the specified range
            Marshal.printf("no free block in the specified range\n");
            return 0;
        }

        blockEnd = findBit(blockStart, maxSlots, 1);

        // Marshal.printf("blockStart: %d, blockEnd: %d\n", blockStart, blockEnd);

        return blockEnd - blockStart;
    }

    /**
     * Find a bit of the given value in the bitmap.
     * @param firstSlot the slot to start seaching at
     * @param maxSlots maximum number of slots to search
     * @param value the slot value to search for
     * @return bit position in the bitmap, or firstSlot+maxSlots if the value could not be found
     */
    @NoHeapAllocation
    public static int findBit(int firstSlot, int maxSlots, int value) {
        int negValue = (value == 0) ? 0xffffffff : 0;
        int offsetBlock = firstSlot / getBlockSize();
        int offsetBit = firstSlot % getBlockSize();
        int pos;

        // Marshal.printf("findBit: offsetBlock %d, offsetBit %d, value %d\n", offsetBlock, offsetBit, value);
        /* the start is not integer aligned */
        if (offsetBit > 0) {
            pos = searchInt(offsetBlock, offsetBit, value, maxSlots);
            if (pos >= 0) {
                return firstSlot + pos;
            }

            pos = -pos;

            firstSlot += pos;
            maxSlots -= pos;
            offsetBlock++;
        }

        /* process full integers */
        while (maxSlots >= getBlockSize()) {
            if (rawGetBitmap(offsetBlock) != negValue) {
                // this int contains searched bit
                break;
            }

            offsetBlock++;
            firstSlot += getBlockSize();
            maxSlots -= getBlockSize();
        }

        if (maxSlots > 0) {
            pos = searchInt(offsetBlock, 0, value, maxSlots);
            if (pos >= 0) {

                return offsetBlock * getBlockSize() + pos;
            }
            pos = -pos;
            firstSlot += pos;
        }

        return firstSlot;
    }

    /**
     * Search a bit value in one entry of the underlying bitmap array.
     * @param offsetBlock block of the bitmap array to be searched for
     * @param offsetBit bit to start searching at
     * @param value value to search for (1 or 0)
     * @param maxSlots maximum number of slots to search
     * @return the bit in the bitmap array entry of the first occurence of the value
     */
    @NoHeapAllocation
    private static int searchInt(int offsetBlock, int offsetBit, int value, int maxSlots) {
        int bitsSearched = 0;

        offsetBit = getBlockSize() - offsetBit;
        int i = offsetBit;
        if (offsetBit > maxSlots) {
            i = maxSlots;
        }

        while (i-- > 0) {
            if (((rawGetBitmap(offsetBlock) >> --offsetBit) & 1) == value) {
                return bitsSearched;
            } else {
                bitsSearched++;
            }
        }

        // nothing found
        return -bitsSearched;
    }

    /**
     * convert an object address to the start slot of this object. Attention: Does not check if the object is on the
     * heap that this bitmap is used for!
     * @param dom the domain of the heap to be used as a start address
     * @param o the object to get the start slot from
     * @return the slot the object starts at
     */
    @NoHeapAllocation
    private static int addr2Slot(CoffeeDomain dom, Object o) {
        int address = objectAddress(o);

        return (address - dom.getHeapBegin())/dom.getSlotSize();
    }

    /**
     * Get the raw address of the object in memory
     * @param o the object
     * @return an integer containing the raw address of o
     */
    @NoHeapAllocation
    private static int objectAddress(Object o) {
        // weavelet
        return 0;
    }

    /**
     * Starting at firstSlot, mark slotCount slots in the bitmap as used.
     * @param firstSlot the slot to start marking at (included)
     * @param slotCount the number of slots to mark as used
     */
    @NoHeapAllocation
    public static void markSlots(int firstSlot, int slotCount) {
        // juint type used for the
        int blockSize = getBlockSize();
        int offsetBlock = firstSlot / blockSize;
        int offsetBits = firstSlot % blockSize;

        Marshal.printf("markSlots: from %d on %d slots\n", firstSlot, slotCount);

        if (offsetBits > 0) {
            // offset in the block
            offsetBits = blockSize - offsetBits;
            // i is the number of bits to occupy in the block
            int i = offsetBits;
            if (i > slotCount) {
                i = slotCount;
            }
            slotCount -= i;

            while (i-- > 0) {
                int mask = (1 << --offsetBits);
                rawOr(offsetBlock, mask);
            }
            offsetBlock++;
        }

        while (slotCount >= blockSize) {
            slotCount -= blockSize;
            rawOr(offsetBlock++, ~0);
        }

        for (int i = blockSize; slotCount > 0; slotCount--) {
            rawOr(offsetBlock, 1 << --i);
        }
    }

    /**
     * Accesses the underlying bitmap structure and performs a logic or on the entry starting at the given offset using the mask.
     * @param offset offset in the bitmap array that should be or'd
     * @param mask the mask to use for the logical or
     */
    @NoHeapAllocation
    private static void rawOr(int offset, int mask) {
        // weavelet
    }

    /**
     * Accesses the underlying bitmap structure and sets a value at the give offset
     * @param offset offset n the bitmap array to set the value at
     * @param value value to set in the bitmap
     */
    @NoHeapAllocation
    private static void rawSet(int offset, int value) {
        // weavelet
    }

    /**
     * Gets a value from the bitmap from the given offset
     * @param offset offset in the bitmap array
     * @return the integer value stored at the offset
     */
    @NoHeapAllocation
    private static int rawGetBitmap(int offset) {
        // weavelet
        return 0;
    }

    /**
     * Determine the size of a bitmap block; the call will be replaced in-place by the weavelet!
     * @return the size of a block of the bitmap in bytes (aka sizeof(juint))
     */
    @NoHeapAllocation
    private static int getBlockSize() {
        // weavelet
        return 0;
    }

    /**
     * Calculate the heap address referenced by the slot in the heap of the given domain.
     * @param dom domain whose heap should be used
     * @param slotNo number of slot whose address should be calculated
     * @return the raw address of the slot on the heap
     */
    @NoHeapAllocation
    public static int slotToAddress(CoffeeDomain dom, int slotNo) {
        int address = dom.getHeapBegin() + slotNo * 8;
        return address;
    }

    /**
     * Sets all entries of the bitmap to "free".
     */
    @NoHeapAllocation
    public static void resetBitmap() {
        for (int i = 0; i < getSlotCount(); i++) {
            rawSet(i, 0);
        }
    }

    /**
     * Get the number of slots of the bitmap.
     * @return the number of slots in the bitmap.
     */
    @NoHeapAllocation
    public static int getSlotCount() {
        // weavelet
        return 0;
    }

    /**
     * Print <code>nBlocks</code> blocks from the coffee bitmap to standard out.
     * @param nBlocks number of blocks (from the start) to be printed.
     */
    @NoHeapAllocation
    public static void debug(int nBlocks) {
        Marshal.printf("BITMAP DEBUG:\n");
        for (int i = 0; i < nBlocks; i++) {
            Marshal.printf("[%d]: %x ", i, rawGetBitmap(i));
        }
        Marshal.printf("\n");
    }

}
