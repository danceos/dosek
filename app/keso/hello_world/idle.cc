#include "os/os.h"

void PreIdleHook() {
	kout << "SUCCESS 1 ALL OK" << endl;
	ShutdownMachine();
}
