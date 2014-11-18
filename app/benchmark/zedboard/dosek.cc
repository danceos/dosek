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
#include "crc32.h"


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

uint32_t pulse_checksum_1;
uint32_t pulse_checksum_2;
uint32_t pulse_checksum_3;

#define MAX_PULSES 1500
#define EXPECTED_CHECKSUM 0x69913698
uint32_t pulse_counter_1;
uint32_t pulse_counter_2;
uint32_t pulse_counter_3;

bool parity_error = false;

extern "C" {
    //! Address of the first global constructor (Defined by the linker script)
    extern char __DATA_START;
    //! Address of the last global constructor (Defined by the linker script)
    extern volatile char __DATA_END;
}

extern char _erom, _data, _edata, _bstart, _bend;

#define macro_str(a) _macro_str(a)
#define _macro_str(a) __macro_str(a)
#define __macro_str(a) #a

void os_main(void) {
	Machine::switch_mode(Machine::USER);

	kout << "BBBBBB [[[[[[ "
#ifdef ENCODED
		 << "ENC=1 "
#else
		 << "enc=0 "
#endif
		 << macro_str(GENERATOR_ARGS)
		 << " ]]]]]]" << endl;
	kout << "INI" << endl;

	arch::Timer::set_periodic(50);

    StartOS(0);
}

void __OS_StartOS_dispatch(uint32_t x);

ISR2(reboot) {
	/* Copy Initialized data */
	run_constructors();

	/* Initialize the Parity Error Detector */
	parity_error = false;

	/* Initialize the Counters */
	pulse_checksum_1 = pulse_checksum_2 = pulse_checksum_3 = 0;
	pulse_counter_1 = pulse_counter_2 = pulse_counter_3 = 0;

	volatile uint32_t * L2CCAuxControlReg = (uint32_t *)L2CCAuxCrtl;
	// Check whether the L2 Parity is enabled
	if (*L2CCAuxControlReg & L2CCParityEnable) {
		kout << "L2 Parity is Enabled!!! AuxRegister 0x" << hex << *L2CCAuxControlReg << dec << endl;
	}

	asm volatile("blx os_main");
}

uint32_t TMR_vote(uint32_t a, uint32_t b, uint32_t c) {
	if (a == b) {
		return a;
	} else if (b == c) {
		return b;
	} else if (a == c) {
		return c;
	} else {
		CALL_HOOK(FaultDetectedHook, APPdetected, a, b);
		return 0;
	}
}

extern const uint16_t number_of_tasks;
extern uint16_t pulse_counter_by_task[];


void Pulse(uint32_t idx, uint32_t data) {
	// Update the Checksum
	uint32_t pulse_checksum = TMR_vote
		(pulse_checksum_1, pulse_checksum_2, pulse_checksum_3);

	pulse_checksum = crc32(pulse_checksum, (unsigned char *) &idx, sizeof(idx));
	pulse_checksum = crc32(pulse_checksum, (unsigned char *) &data, sizeof(data));

	pulse_checksum_1 = pulse_checksum;
	pulse_checksum_2 = pulse_checksum;
	pulse_checksum_3 = pulse_checksum;

	// Increment the pulse counter
	uint32_t pulse_counter = TMR_vote
		(pulse_counter_1, pulse_counter_2, pulse_counter_3);
	pulse_counter++;
	pulse_counter_by_task[idx] ++;
	if (pulse_counter > MAX_PULSES) {
		/* End of Test-Run */
		if (pulse_checksum == EXPECTED_CHECKSUM) {
			kout << "EEEEEE [[[[[[ OK OK OK OK " << hex << pulse_checksum
				 << " ]]]]]]" << endl;
			kout << "OK" << endl;
		} else {
			kout << "EEEEEE [[[[[[ SDC SDC SDC " << hex << pulse_checksum
				 << " ]]]]]]" << endl;
			kout << "FL EXC" << endl;
			int never_activated = 0;
			for (int i = 0; i < number_of_tasks; i++) {
				kout <<"0x" << hex << i << ": 0x" << pulse_counter_by_task[i] << endl;
				if (pulse_counter_by_task[i] == 0)
					never_activated ++;
			}
			kout << "Never activated: " << dec << never_activated << endl;
		}

		/* Restart the benchmark */
		Machine::trigger_interrupt_from_user(5);
		while(1) {};
	}

	pulse_counter_1 = pulse_counter;
	pulse_counter_2 = pulse_counter;
	pulse_counter_3 = pulse_counter;
}

/* From Hacker's Delight p. 66; Figure 5-2 */
static int pop(unsigned x)
{
    x = x - ((x >> 1) & 0x55555555);
    x = (x & 0x33333333) + ((x >> 2) & 0x33333333);
    x = (x + (x >> 4)) & 0x0F0F0F0F;
    x = x + (x >> 8);
    x = x + (x >> 16);
    return x & 0x0000003F;
}

uint32_t Calc(uint32_t idx, uint32_t data) {
	return pop(pop(idx) * pop(data)) | ((idx + data) << 16);
}

DeclareResource(RES_SCHEDULER);

#include "dosek-tasks.cc"

FaultDetectedHook() {
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

