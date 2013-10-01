#include "output.h"

output_t kout;

void os_main(void) {
	kout.setcolor(CGA::RED, CGA::WHITE);
	kout << "CoRedOS start" << endl;
	kout.setcolor(CGA::WHITE, CGA::BLACK);

	// TODO do stuff

	kout.setcolor(CGA::RED, CGA::WHITE);
	kout << "CoRedOS halt" << endl;

	for(;;) {
        __asm__ ("nop");
    }
}

