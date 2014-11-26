/**
 * @file
 * @ingroup ARM
 * @brief Reset operation
 */

#include "machine.h"
#include "hal_cache.h"

#define SLCR_UNLOCK_MAGIC       0xDF0D
#define SLCR_UNLOCK_OFFSET      0x8   /* SCLR unlock register */
#define SLCR_REBOOT_STATUS_OFFSET   0x258 /* PS Reboot Status */
#define SLCR_PS_RST_CTRL_OFFSET     0x200 /* PS Software Reset Control */
#define SLCR_BASE_ADDRESS 0xF8000000

__attribute__((always_inline)) inline static uint32_t Xil_In32(uint32_t Addr)
{
	return *(volatile uint32_t *) Addr;
}

__attribute__((always_inline)) inline static void Xil_Out32(uint32_t OutAddress, uint32_t Value)
{
	*(volatile uint32_t *) OutAddress = Value;
}


static void zynq_slcr_write(uint32_t val, uint32_t offset) {
	Xil_Out32(SLCR_BASE_ADDRESS + offset, val);
}

static void zynq_slcr_read(uint32_t* val, uint32_t offset) {
    *val = Xil_In32(SLCR_BASE_ADDRESS + offset);
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

/****************************************************************************/
/**
*
* L2 Cache Control
* ================
* from Xilinx14.7/14.7/ISE_DS/EDK/sw/lib/bsp/standalone_v3_11_a/src/cortexa9
*
*
*****************************************************************************/

/************************** Constant Definitions *****************************/
/* L2CC Register Offsets */
#define XPS_L2CC_ID_OFFSET		0x0000
#define XPS_L2CC_TYPE_OFFSET		0x0004
#define XPS_L2CC_CNTRL_OFFSET		0x0100
#define XPS_L2CC_AUX_CNTRL_OFFSET	0x0104
#define XPS_L2CC_TAG_RAM_CNTRL_OFFSET	0x0108
#define XPS_L2CC_DATA_RAM_CNTRL_OFFSET	0x010C

#define XPS_L2CC_EVNT_CNTRL_OFFSET	0x0200
#define XPS_L2CC_EVNT_CNT1_CTRL_OFFSET	0x0204
#define XPS_L2CC_EVNT_CNT0_CTRL_OFFSET	0x0208
#define XPS_L2CC_EVNT_CNT1_VAL_OFFSET	0x020C
#define XPS_L2CC_EVNT_CNT0_VAL_OFFSET	0x0210

#define XPS_L2CC_IER_OFFSET		0x0214		/* Interrupt Mask */
#define XPS_L2CC_IPR_OFFSET		0x0218		/* Masked interrupt status */
#define XPS_L2CC_ISR_OFFSET		0x021C		/* Raw Interrupt Status */
#define XPS_L2CC_IAR_OFFSET		0x0220		/* Interrupt Clear */

#define XPS_L2CC_CACHE_SYNC_OFFSET		0x0730		/* Cache Sync */
#define XPS_L2CC_DUMMY_CACHE_SYNC_OFFSET	0x0740		/* Dummy Register for Cache Sync */
#define XPS_L2CC_CACHE_INVLD_PA_OFFSET		0x0770		/* Cache Invalid by PA */
#define XPS_L2CC_CACHE_INVLD_WAY_OFFSET		0x077C		/* Cache Invalid by Way */
#define XPS_L2CC_CACHE_CLEAN_PA_OFFSET		0x07B0		/* Cache Clean by PA */
#define XPS_L2CC_CACHE_CLEAN_INDX_OFFSET	0x07B8		/* Cache Clean by Index */
#define XPS_L2CC_CACHE_CLEAN_WAY_OFFSET		0x07BC		/* Cache Clean by Way */
#define XPS_L2CC_CACHE_INV_CLN_PA_OFFSET	0x07F0		/* Cache Invalidate and Clean by PA */
#define XPS_L2CC_CACHE_INV_CLN_INDX_OFFSET	0x07F8		/* Cache Invalidate and Clean by Index */
#define XPS_L2CC_CACHE_INV_CLN_WAY_OFFSET	0x07FC		/* Cache Invalidate and Clean by Way */

#define XPS_L2CC_CACHE_DLCKDWN_0_WAY_OFFSET	0x0900		/* Cache Data Lockdown 0 by Way */
#define XPS_L2CC_CACHE_ILCKDWN_0_WAY_OFFSET	0x0904		/* Cache Instruction Lockdown 0 by Way */
#define XPS_L2CC_CACHE_DLCKDWN_1_WAY_OFFSET	0x0908		/* Cache Data Lockdown 1 by Way */
#define XPS_L2CC_CACHE_ILCKDWN_1_WAY_OFFSET	0x090C		/* Cache Instruction Lockdown 1 by Way */
#define XPS_L2CC_CACHE_DLCKDWN_2_WAY_OFFSET	0x0910		/* Cache Data Lockdown 2 by Way */
#define XPS_L2CC_CACHE_ILCKDWN_2_WAY_OFFSET	0x0914		/* Cache Instruction Lockdown 2 by Way */
#define XPS_L2CC_CACHE_DLCKDWN_3_WAY_OFFSET	0x0918		/* Cache Data Lockdown 3 by Way */
#define XPS_L2CC_CACHE_ILCKDWN_3_WAY_OFFSET	0x091C		/* Cache Instruction Lockdown 3 by Way */
#define XPS_L2CC_CACHE_DLCKDWN_4_WAY_OFFSET	0x0920		/* Cache Data Lockdown 4 by Way */
#define XPS_L2CC_CACHE_ILCKDWN_4_WAY_OFFSET	0x0924		/* Cache Instruction Lockdown 4 by Way */
#define XPS_L2CC_CACHE_DLCKDWN_5_WAY_OFFSET	0x0928		/* Cache Data Lockdown 5 by Way */
#define XPS_L2CC_CACHE_ILCKDWN_5_WAY_OFFSET	0x092C		/* Cache Instruction Lockdown 5 by Way */
#define XPS_L2CC_CACHE_DLCKDWN_6_WAY_OFFSET	0x0930		/* Cache Data Lockdown 6 by Way */
#define XPS_L2CC_CACHE_ILCKDWN_6_WAY_OFFSET	0x0934		/* Cache Instruction Lockdown 6 by Way */
#define XPS_L2CC_CACHE_DLCKDWN_7_WAY_OFFSET	0x0938		/* Cache Data Lockdown 7 by Way */
#define XPS_L2CC_CACHE_ILCKDWN_7_WAY_OFFSET	0x093C		/* Cache Instruction Lockdown 7 by Way */

#define XPS_L2CC_CACHE_LCKDWN_LINE_ENABLE_OFFSET 0x0950		/* Cache Lockdown Line Enable */
#define XPS_L2CC_CACHE_UUNLOCK_ALL_WAY_OFFSET	0x0954		/* Cache Unlock All Lines by Way */

#define XPS_L2CC_ADDR_FILTER_START_OFFSET	0x0C00		/* Start of address filtering */
#define XPS_L2CC_ADDR_FILTER_END_OFFSET		0x0C04		/* Start of address filtering */

#define XPS_L2CC_DEBUG_CTRL_OFFSET		0x0F40		/* Debug Control Register */

/* XPS_L2CC_CNTRL_OFFSET bit masks */
#define XPS_L2CC_ENABLE_MASK		0x00000001	/* enables the L2CC */

/* XPS_L2CC_AUX_CNTRL_OFFSET bit masks */
#define XPS_L2CC_AUX_EBRESPE_MASK	0x40000000	/* Early BRESP Enable */
#define XPS_L2CC_AUX_IPFE_MASK		0x20000000	/* Instruction Prefetch Enable */
#define XPS_L2CC_AUX_DPFE_MASK		0x10000000	/* Data Prefetch Enable */
#define XPS_L2CC_AUX_NSIC_MASK		0x08000000	/* Non-secure interrupt access control */
#define XPS_L2CC_AUX_NSLE_MASK		0x04000000	/* Non-secure lockdown enable */
#define XPS_L2CC_AUX_CRP_MASK		0x02000000	/* Cache replacement policy */
#define XPS_L2CC_AUX_FWE_MASK		0x01800000	/* Force write allocate */
#define XPS_L2CC_AUX_SAOE_MASK		0x00400000	/* Shared attribute override enable */
#define XPS_L2CC_AUX_PE_MASK		0x00200000	/* Parity enable */
#define XPS_L2CC_AUX_EMBE_MASK		0x00100000	/* Event monitor bus enable */
#define XPS_L2CC_AUX_WAY_SIZE_MASK	0x000E0000	/* Way-size */
#define XPS_L2CC_AUX_ASSOC_MASK		0x00010000	/* Associativity */
#define XPS_L2CC_AUX_SAIE_MASK		0x00002000	/* Shared attribute invalidate enable */
#define XPS_L2CC_AUX_EXCL_CACHE_MASK	0x00001000	/* Exclusive cache configuration */
#define XPS_L2CC_AUX_SBDLE_MASK		0x00000800	/* Store buffer device limitation Enable */
#define XPS_L2CC_AUX_HPSODRE_MASK	0x00000400	/* High Priority for SO and Dev Reads Enable */
#define XPS_L2CC_AUX_FLZE_MASK		0x00000001	/* Full line of zero enable */

#define XPS_L2CC_AUX_REG_DEFAULT_MASK	0x72360000	/* Enable all prefetching, */
                                                    /* Cache replacement policy, Parity enable, */
                                                    /* Event monitor bus enable and Way Size (64 KB) */
#define XPS_L2CC_AUX_REG_ZERO_MASK	0xFFF1FFFF	/* */

#define XPS_L2CC_TAG_RAM_DEFAULT_MASK	0x00000111	/* latency for TAG RAM */
#define XPS_L2CC_DATA_RAM_DEFAULT_MASK	0x00000121	/* latency for DATA RAM */

/* Interrupt bit masks */
#define XPS_L2CC_IXR_DECERR_MASK	0x00000100	/* DECERR from L3 */
#define XPS_L2CC_IXR_SLVERR_MASK	0x00000080	/* SLVERR from L3 */
#define XPS_L2CC_IXR_ERRRD_MASK		0x00000040	/* Error on L2 data RAM (Read) */
#define XPS_L2CC_IXR_ERRRT_MASK		0x00000020	/* Error on L2 tag RAM (Read) */
#define XPS_L2CC_IXR_ERRWD_MASK		0x00000010	/* Error on L2 data RAM (Write) */
#define XPS_L2CC_IXR_ERRWT_MASK		0x00000008	/* Error on L2 tag RAM (Write) */
#define XPS_L2CC_IXR_PARRD_MASK		0x00000004	/* Parity Error on L2 data RAM (Read) */
#define XPS_L2CC_IXR_PARRT_MASK		0x00000002	/* Parity Error on L2 tag RAM (Read) */
#define XPS_L2CC_IXR_ECNTR_MASK		0x00000001	/* Event Counter1/0 Overflow Increment */

/* Address filtering mask and enable bit */
#define XPS_L2CC_ADDR_FILTER_VALID_MASK	0xFFF00000	/* Address filtering valid bits*/
#define XPS_L2CC_ADDR_FILTER_ENABLE_MASK 0x00000001	/* Address filtering enable bit*/

/* Debug control bits */
#define XPS_L2CC_DEBUG_SPIDEN_MASK	0x00000004	/* Debug SPIDEN bit */
#define XPS_L2CC_DEBUG_DWB_MASK		0x00000002	/* Debug DWB bit, forces write through */
#define XPS_L2CC_DEBUG_DCL_MASK		0x00000002	/* Debug DCL bit, disables cache line fill */


#define XPS_L2CC_BASEADDR		0xF8F02000

/****************************************************************************
*
* Perform L2 Cache Sync Operation.
*
* @param	None.
*
* @return	None.
*
* @note		None.
*
****************************************************************************/
static inline void Xil_L2CacheSync(void) {
#ifdef CONFIG_PL310_ERRATA_753970
	Xil_Out32(XPS_L2CC_BASEADDR + XPS_L2CC_DUMMY_CACHE_SYNC_OFFSET, 0x0);
#else
	Xil_Out32(XPS_L2CC_BASEADDR + XPS_L2CC_CACHE_SYNC_OFFSET, 0x0);
#endif
}


/****************************************************************************
*
* Invalidate the L2 cache. If the byte specified by the address (adr)
* is cached by the Data cache, the cacheline containing that byte is
* invalidated.	If the cacheline is modified (dirty), the modified contents
* are lost and are NOT written to system memory before the line is
* invalidated.
*
* @param	Address to be flushed.
*
* @return	None.
*
* @note		The bottom 4 bits are set to 0, forced by architecture.
*
****************************************************************************/
void Xil_L2CacheInvalidate(void)
{
	/* Invalidate the caches */
	Xil_Out32(XPS_L2CC_BASEADDR + XPS_L2CC_CACHE_INVLD_WAY_OFFSET,
		  0x0000FFFF);
	while((Xil_In32(XPS_L2CC_BASEADDR + XPS_L2CC_CACHE_INVLD_WAY_OFFSET))
																& 0x0000FFFF);

	/* Wait for the invalidate to complete */
	Xil_L2CacheSync();

	/* synchronize the processor */
	dsb();
}


void Xil_L2CacheEnable(void)
{
	unsigned int L2CCReg;

	L2CCReg = Xil_In32(XPS_L2CC_BASEADDR + XPS_L2CC_CNTRL_OFFSET);

	/* only enable if L2CC is currently disabled */
	if ((L2CCReg & 0x01) == 0) {
		/* set up the way size and latencies */
		L2CCReg = Xil_In32(XPS_L2CC_BASEADDR +
				   XPS_L2CC_AUX_CNTRL_OFFSET);
		L2CCReg &= XPS_L2CC_AUX_REG_ZERO_MASK; // clear way-size
		L2CCReg |= XPS_L2CC_AUX_REG_DEFAULT_MASK;
		L2CCReg &= (~XPS_L2CC_AUX_PE_MASK); // disable parity (default)
		Xil_Out32(XPS_L2CC_BASEADDR + XPS_L2CC_AUX_CNTRL_OFFSET,
			  L2CCReg);
		Xil_Out32(XPS_L2CC_BASEADDR + XPS_L2CC_TAG_RAM_CNTRL_OFFSET,
			  XPS_L2CC_TAG_RAM_DEFAULT_MASK);
		Xil_Out32(XPS_L2CC_BASEADDR + XPS_L2CC_DATA_RAM_CNTRL_OFFSET,
			  XPS_L2CC_DATA_RAM_DEFAULT_MASK);

		/* FIXME: this shouldn't be the default! */
		/* lockdown: enable/disable data/instruction caching for each core */
		/* CPU0: enable data, disable instruction caching */
		Xil_Out32(XPS_L2CC_BASEADDR + XPS_L2CC_CACHE_ILCKDWN_0_WAY_OFFSET,
			 0x0000FFFF);

		/* CPU1: disable both data and instructions caching */
		Xil_Out32(XPS_L2CC_BASEADDR + XPS_L2CC_CACHE_DLCKDWN_1_WAY_OFFSET,
			 0x0000FFFF);
		Xil_Out32(XPS_L2CC_BASEADDR + XPS_L2CC_CACHE_ILCKDWN_1_WAY_OFFSET,
			 0x0000FFFF);

		/* Clear the pending interrupts */
		L2CCReg = Xil_In32(XPS_L2CC_BASEADDR +
				   XPS_L2CC_ISR_OFFSET);
		Xil_Out32(XPS_L2CC_BASEADDR + XPS_L2CC_IAR_OFFSET, L2CCReg);

		Xil_L2CacheInvalidate();
		/* Enable the L2CC */
		L2CCReg = Xil_In32(XPS_L2CC_BASEADDR +
				   XPS_L2CC_CNTRL_OFFSET);
		Xil_Out32(XPS_L2CC_BASEADDR + XPS_L2CC_CNTRL_OFFSET,
			  (L2CCReg | (0x01)));

        Xil_L2CacheSync();
        /* synchronize the processor */
	    dsb();

    }
}


void Machine::setup_caches(void) {

    // Invalidate caches
    HAL_DCACHE_INVALIDATE_ALL();
    HAL_ICACHE_INVALIDATE_ALL();

	// Enable Caches
	HAL_DCACHE_ENABLE();
	HAL_ICACHE_ENABLE();

    // Disable parity checking for the L1 cache.
    // This setting should be default, anyway.
    asm volatile (  "MRC p15, 0,r1, c1, c0, 1;"
                    "orr r1, r1, #0x200;"
                    "MCR p15, 0,r1, c1, c0, 1"
        :
        :
        : "r1" /* Clobber list */
        );

    // Enable the L2 cache
    Xil_L2CacheEnable();
}

