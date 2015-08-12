#ifndef __ALARM3_COMMON_H__
#define __ALARM3_COMMON_H__

#define WAIT_FOR_IRQ() do{ stop = false; \
	for (volatile unsigned long long counter = 0, stop = false;			\
		 stop == false && counter < max_count;							\
		 counter++) {}													\
	} while(0);

#endif
