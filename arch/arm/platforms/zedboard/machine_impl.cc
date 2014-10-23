/**
 * @file
 * @ingroup ARM
 * @brief Reset operation
 */

#include "machine.h"

#define SLCR_UNLOCK_MAGIC       0xDF0D
#define SLCR_UNLOCK_OFFSET      0x8   /* SCLR unlock register */
#define SLCR_REBOOT_STATUS_OFFSET   0x258 /* PS Reboot Status */
#define SLCR_PS_RST_CTRL_OFFSET     0x200 /* PS Software Reset Control */
#define SLCR_BASE_ADDRESS 0xF8000000

static void zynq_slcr_write(uint32_t val, uint32_t offset) {
    *(volatile uint32_t*)(SLCR_BASE_ADDRESS + offset) = val;
}

static void zynq_slcr_read(uint32_t* val, uint32_t offset) {
    *val = *(volatile uint32_t*)(SLCR_BASE_ADDRESS + offset);
}
void Machine::reset(void) {
    uint32_t reboot;
    /**
     * Unlock SLCR then reset system.
     * This seems to require raw i/o, or there's a lockup?!
     */

    zynq_slcr_write(SLCR_UNLOCK_MAGIC, SLCR_UNLOCK_OFFSET);

    zynq_slcr_read(&reboot, SLCR_REBOOT_STATUS_OFFSET);
    zynq_slcr_write(reboot & 0xF0FFFFFF, SLCR_REBOOT_STATUS_OFFSET);
    zynq_slcr_write(1, SLCR_PS_RST_CTRL_OFFSET);
}



