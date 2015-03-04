#include "os/os.h"

void ShutdownHook(StatusType status) {
	if (status == E_OK)
		kout << "SUCCESS 1 ALL OK" << endl;
	else
		kout << "FAIL" << endl;
}
