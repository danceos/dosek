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
import keso.coffeebreak.*;

public class CoffeeBreakCollector {
    /**
     * @param did domain id of the domain to be garbage collected
     * @return 1 if collection was executed, 0 if not
     */
    @NoHeapAllocation
    public static int JavaCoffeeBreakMain(int did) {
        CoffeeDomain dom = new CoffeeDomain(did);

        if (gcNeed(dom) <= 0) {
            Marshal.printf("gc run triggered\n");

            GCUtils.lock();

            dom.toggleColorBit();

            // MARK
            for (int i = 0; i < CoffeeBlocking.getNumBlockingTasks(); i++) {
                Marshal.printf("Scanning blocking task %d\n", i);
                processStack(dom, i);
            }

            for (int i = 0; i < GCUtils.getRootSetSize(); i++) {
                Object rootObject = dom.rootObjectAt(i);
                pushObject(dom, rootObject);
            }

            while (!CoffeeStack.isEmpty()) {
                scanObject(dom, CoffeeStack.pop());
            }

            // uncomment for extra sweep() testing fun
            /*
            Marshal.printf("TODO remove: marking 10, 32 and 74 slots for debug\n");
            CoffeeBitmap.markSlots(10, 10);
            CoffeeBitmap.markSlots(64, 32);
            CoffeeBitmap.markSlots(120, 74);
            */


            // SWEEP
            sweep(dom);

            // for the next run we need a fresh bitmap
            CoffeeBitmap.resetBitmap();

            GCUtils.unlock();

            // TODO remove if not debugging
            Marshal.error("gc ran to end\n");
            return 1;
        }
        return 0;
    }

    @NoHeapAllocation
    private static void processStack(CoffeeDomain dom, int taskNumber) {
        CoffeeTaskStack stack = new CoffeeTaskStack();
        stack = CoffeeBlocking.getStackByTask(taskNumber, stack);

        for ( ; !stack.atEnd(); stack.next()) {
            if (stack.checkDomain(dom)) {
                CoffeeLLRefStack llref = new CoffeeLLRefStack();
                llref = stack.getLLRefs(llref);

                if (llref.isEmptyStack()) {
                    continue;
                }

                while (!llref.atEnd()) {
                    if (llref.currentObject() == null) {
                        llref.nextObject();
                    } else if (llref.isStackRef())  {
                        llref.nextFrame();
                    } else {
                        pushObject(dom, llref.currentObject());
                        llref.nextObject();
                    }
                }
            }
        }
    }

    @NoHeapAllocation
    private static void pushObject(CoffeeDomain dom, Object o) {
        if (o == null) {
            return;
        }

        if (!dom.isObjectColored(o)) {
            dom.colorObject(o);
            CoffeeStack.push(o);
        }
    }

    @NoHeapAllocation
    private static void scanObject(CoffeeDomain dom, Object o) {
        int curRef;

        if (o == null) {
            return;
        }

        curRef = dom.refCount(o);

        /* Detection if "normal" indexing into references via negative offset is used (negative curRef)
         * or the object array extension (extra array for references, positive curRef) is available
         */
        if (curRef > 0) {
            // object array capable
            while (curRef > 0) {
                pushObject(dom, dom.getReference(o, curRef--));
            }
        } else if (curRef < 0) {
            // negative offset into object
            while (curRef < 0) {
                pushObject(dom, dom.getReference(o, curRef++));
            }
        }

        // TODO remove as soon as SideEffectAnalysis is fixed
        int trash = CoffeeBitmap.markObject(dom, o);
    }

    @NoHeapAllocation
    private static void sweep(CoffeeDomain dom) {
        CoffeeListElement elem = new CoffeeListElement(dom);
        int currentSlot = 0;
        int numSlots = CoffeeBitmap.getSlotCount();

        /*
        Marshal.printf("Starting sweep run\n");
        Marshal.printf("numSlots %d\n", numSlots);
        Marshal.printf("heapBegin: %x\n", dom.getHeapBegin());
        Marshal.printf("heapEnd: %x\n", dom.getHeapBegin() + dom.getHeapSize());
        */

        elem.clearList();
        dom.setHeapFree(0);

        // Marshal.printf("List was emptied\n");
        int recoveredBlocks = 0;

        while (currentSlot < numSlots) {
            //int slotsInBlock = CoffeeBitmap.findFreeBlock(currentSlot, numSlots - currentSlot);
            int freeStart = CoffeeBitmap.findBit(currentSlot, numSlots - currentSlot, 0);
            int freeEnd = CoffeeBitmap.findBit(freeStart, numSlots - freeStart, 1);
            int slotsInBlock = freeEnd - freeStart;

            // Marshal.printf("Size: %d, freeStart: %d, freeEnd: %d\n", slotsInBlock, freeStart, freeEnd);

            if (slotsInBlock > 0) {
                int blockSize = slotsInBlock * dom.getSlotSize();
                int startAddress = CoffeeBitmap.slotToAddress(dom, freeStart);

                // FIXME: Only if KESO_HAS_TINY_SLOTS
                if (blockSize >= elem.rawStructSize()) {
                    // Marshal.printf("Size: %d, freeStart: %d, freeEnd: %d\n", slotsInBlock, freeStart, freeEnd);
                    // Marshal.printf("StartAddress %x\n", startAddress);
                    recoveredBlocks += slotsInBlock;

                    elem.append(startAddress, slotsInBlock);

                    dom.setHeapFree(dom.getHeapFree() + blockSize);
                }

                currentSlot = freeEnd;
                // Marshal.printf("currentSlot: %d\n", currentSlot);
            }
        }

        elem.debugPrint();

        Marshal.printf("Recovered %d slots in sweep()\n", recoveredBlocks);
    }

    /**
     * Determine if garbage collection is needed
     * @param domain
     * @return negative number if gc is needed, positive number or zero else
     */
    @NoHeapAllocation
    private static int gcNeed(CoffeeDomain domain) {
        int need = domain.getHeapFree() - domain.getSasls() - (domain.getHeapSize()/4);

        // TODO remove this: Always GC for debugging
        need = -1;
        if (need < 0) {
            Marshal.printf("gcneed!\n");
        }

        return need;
    }
}
