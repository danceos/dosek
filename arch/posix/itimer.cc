/**
 * @file
 * @ingroup posix
 * @brief POSIX Timer implementation
 */

#include "itimer.h"
#include "machine.h"
#include "os/counter.h"
#include <signal.h>
#include <sys/time.h>

namespace arch {


/** \brief Timer signal handler */
void timer_handler(__attribute__((unused)) int signum) {
	os::Counter::tick();
}

void ITimer::init() {
    /* Install timer_handler as the signal handler for SIGVTALRM. */
	arch::irq.set_handler(SIGALRM, timer_handler);
	arch::irq.enable(SIGALRM);
	arch::irq.set_handler(SIGVTALRM, timer_handler);
	arch::irq.enable(SIGVTALRM);

	// generate signal @ 1 kHz
	set_periodic(1000);
}


void ITimer::set_periodic(uint16_t rateHz) {
    time_t secs = 0;
    suseconds_t usecs = 0;

    if( rateHz == 1 ){
        secs = 1;
    } else {
        float period_in_us = (1000000. / rateHz);
        usecs = static_cast<suseconds_t>(period_in_us);
    }

    struct itimerval timer;

    /* initial phase */
    timer.it_value.tv_sec = secs;
    timer.it_value.tv_usec = usecs;

    /* period */
    timer.it_interval.tv_sec = secs;
    timer.it_interval.tv_usec = usecs;

    /* start timer: counting whenever process is executing! */
    if(setitimer(ITIMER_REAL, &timer, NULL) == -1 ) {
        kout << "setitimer failed in set_periodic." << endl;
        exit(EXIT_FAILURE);
    }
}

}; // namespace arch
