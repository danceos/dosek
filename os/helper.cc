#include "machine.h"
#include "os/helper.h"

void ShutdownMachine(void) {
	Machine::shutdown();
}
