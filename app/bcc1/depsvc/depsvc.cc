

#include "os.h"
#include "depsvc.h"
#include "arch/generic/hardware_threads.h"
#include "output.h"
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

	arch::start_hardware_thread(1, dependability_stack, stacksize, dep::dependability_service);
	StartOS(0);
}

unsigned int datacheck()
{
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
	kout << c << endl;
	if (++c > 10) {
		ShutdownMachine();
	}
	TerminateTask();
}
