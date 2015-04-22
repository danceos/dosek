#include "os.h"
#include "dependability/depsvc.h"
#include "arch/generic/hardware_threads.h"
#include "output.h"
#include "test/test.h"
#include "type.h"

DeclareTask(CheckedTask);
DeclareAlarm(PeriodicActivation);
DeclareCounter(PeriodicActivationCounter);

DeclareCheckedObject(chararray, area);
DeclareCheckedObject(complextype, data);

const unsigned int stacksize = 4096;
char dependability_stack[stacksize];

void os_main()
{
	data.remote = &area;
	test_init();

	arch::start_hardware_thread(1, dependability_stack, stacksize, dep::dependability_service);

	test_start();
	StartOS(0);
}

int checked;

unsigned int datacheck()
{
	checked = 1;
	unsigned int checksum = 0;
	for (unsigned int i = 0; i < sizeof(chararray); ++i) {
		checksum += (*data.remote)[i];
	}
	return checksum;
}

TASK(CheckedTask) {
	static unsigned int c = 0;
	AcquireCheckedObject(area);
	AcquireCheckedObject(data);
	for (unsigned int i = 1; i < sizeof(area); ++i) {
		area[i] = area[i - 1] + 1;
	}
	ReleaseCheckedObject(data);
	ReleaseCheckedObject(area);
	test_trace('0' +  c);
	if (++c > 5) {
#ifdef CONFIG_DEPENDABILITY_FAILURE_LOGGING
		kout << "Dependability Failure Count: " << GET_DEPENDABILITY_FAILURE_COUNT()
			 << "/" << GET_DEPENDABILITY_CHECK_COUNT() << endl;
#endif
		test_trace('0' + checked);
		test_trace_assert("0123451");
		test_finish();
		ShutdownMachine();
	}
	TerminateTask();
}

void PreIdleHook() {
	dep::release_all_CheckedObjects();
}
