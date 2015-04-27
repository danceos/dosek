/**
 * @defgroup apps Applications
 * @brief The applications...
 */

/**
 * @file
 * @ingroup apps
 * @brief Just a simple test application
 */
#include "os.h"
#include "test/test.h"
#include "machine.h"
#include "arch/arm/gic.h"
#include "arch/arm/syscall.h"
#include "arch/arm/timer.h"
#include "arch/arm/constructors.h"


#define PSS_L2CC_BASE_ADDR 0xF8F02000

#define L2CCWay		(PSS_L2CC_BASE_ADDR + 0x077C)	/*(PSS_L2CC_BASE_ADDR + PSS_L2CC_CACHE_INVLD_WAY_OFFSET)*/
#define L2CCSync		(PSS_L2CC_BASE_ADDR + 0x0730)	/*(PSS_L2CC_BASE_ADDR + PSS_L2CC_CACHE_SYNC_OFFSET)*/
#define L2CCCrtl		(PSS_L2CC_BASE_ADDR + 0x0100)	/*(PSS_L2CC_BASE_ADDR + PSS_L2CC_CNTRL_OFFSET)*/
#define L2CCAuxCrtl	(PSS_L2CC_BASE_ADDR + 0x0104)	/*(PSS_L2CC_BASE_ADDR + XPSS_L2CC_AUX_CNTRL_OFFSET)*/
#define L2CCTAGLatReg	(PSS_L2CC_BASE_ADDR + 0x0108)	/*(PSS_L2CC_BASE_ADDR + XPSS_L2CC_TAG_RAM_CNTRL_OFFSET)*/
#define L2CCDataLatReg	(PSS_L2CC_BASE_ADDR + 0x010C)	/*(PSS_L2CC_BASE_ADDR + XPSS_L2CC_DATA_RAM_CNTRL_OFFSET)*/
#define L2CCIntClear	(PSS_L2CC_BASE_ADDR + 0x0220)	/*(PSS_L2CC_BASE_ADDR + XPSS_L2CC_IAR_OFFSET)*/
#define L2CCIntRaw	    (PSS_L2CC_BASE_ADDR + 0x021C)	/*(PSS_L2CC_BASE_ADDR + XPSS_L2CC_ISR_OFFSET)*/

#define L2CCParityEnable (1<<21)

bool parity_error = false;

#define macro_str(a) _macro_str(a)
#define _macro_str(a) __macro_str(a)
#define __macro_str(a) #a

extern int do_matrix();

ISR2(reboot) {
	/* Copy Initialized data */
	run_constructors();

	kout << "RRRRR [[[[[ Reboot Parity=" << parity_error << " ]]]]]" << endl;

	/* Initialize the Parity Error Detector */
	parity_error = false;


	volatile uint32_t * L2CCAuxControlReg = (uint32_t *)L2CCAuxCrtl;
	// Check whether the L2 Parity is enabled
	if (*L2CCAuxControlReg & L2CCParityEnable) {
		kout << "L2 Parity is Enabled!!! AuxRegister 0x" << hex << *L2CCAuxControlReg << dec << endl;
	}

	asm volatile("blx os_main");
}

extern void OS_MM(void);
void StartupHook() {
	arch::Timer::stop();
	arch::syscall(OS_MM);
}

void OS_MM(void){
	kout << "BBBBBB [[[[[[ "
		 << "zedboard-mm "
		 << macro_str(GENERATOR_ARGS)
		 << " ]]]]]]" << endl;
	kout << "INI" << endl;

	int i = 0;
	while (1) {
		bool good = do_matrix();
		if (!good || i++ > 50) {
			//kout << "good = " << &good << endl;
			// Machine::trigger_interrupt_from_user(12);
			OSEKOS_ISR_reboot();
		}
	}
}


TASK(DummyHandler) {
	TerminateTask();
}

void FaultDetectedHook() {
	(void) type;
	(void) arg1;
	(void) arg2;
	kout << "FFFFFF [[[[[[ DET DET DET ]]]]]]" << endl;
	kout << "FL DET ";

	switch (type) {
	case XORdetected:
		kout << "XOR";
		break;
	case DMRdetected:
		kout << "DMR";
		break;
	case ANBdetected:
		kout << "ANB";
		break;
	case PARITYdetected:
		kout << "PAR";
		break;
	case APPdetected:
		kout << "APP" << endl;

		break;
	case TRAPdetected:
		kout << "TRAP";
		break;
	case IRQ_SPURdetected:
		kout << "IRQ_SPUR";
		break;
	case LOGIC_ERRORdetected:
		kout << "LOGIC_ERROR";
		break;
	case STATE_ASSERTdetected:
		kout << "STATE_ASSERT";
		break;
	default:
		kout << "UNKNOWN";
	}
	kout << hex << " 0x" << arg1 << " 0x" << arg2 << " P:" << dec << parity_error << endl;

		int cpsr = Machine::get_cpsr() & 0x1f;
	if (cpsr != Machine::USER) {
		OSEKOS_ISR_reboot();
	} else {
		/* Restart the benchmark */
		arch::GIC::set_task_prio(0xff);
		Machine::trigger_interrupt_from_user(5);
		while(1) {};
	}
}
ISR2(isrA) {
	parity_error = true;
}

ISR2(isrB) {
	parity_error = true;
}

