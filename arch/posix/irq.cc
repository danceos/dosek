#include <string.h>
#include <syscall.h>
#include <unistd.h>

#include "irq.h"
#include "os/scheduler/scheduler.h"

using namespace arch;

static void panic(int signal) {
	kout << "spurious interrupt: " << signal << endl;
}

IRQ::IRQ() {
    for(unsigned int i = 0; i < SIGMAX; i++)
        m_gate[i] = &panic;
	ast_level = 0;
}

void IRQ::set_handler(int signum, irq_handler_t handler) {
    m_gate[signum] = handler;
}

void IRQ::enable(int signum) {
    struct sigaction sig;

    memset(&sig, 0, sizeof(sig));
    sig.sa_handler = guardian;
    sig.sa_flags = SA_RESTART;
	sigfillset(&sig.sa_mask);

    sigaction(signum, &sig, NULL);
}

void IRQ::disable(int signum) {
    struct sigaction sig;

    memset(&sig, 0, sizeof(sig));
    sig.sa_handler = SIG_IGN;
    sig.sa_flags = SA_RESTART;

    sigaction(signum, &sig, NULL);
}

void IRQ::trigger_interrupt(int irq) {
	/* Send an signal to the current thread */
	unsigned int tid = ::syscall(SYS_gettid);
	::syscall(SYS_tgkill, getpid(), tid, irq);
}

void IRQ::disable_interrupts() {
	sigset_t mask;
	sigfillset(&mask);
	syscall(SYS_rt_sigprocmask, SIG_BLOCK, &mask, NULL, 8);
}

void IRQ::enable_interrupts() {
	sigset_t mask;
	sigfillset(&mask);
	syscall(SYS_rt_sigprocmask, SIG_UNBLOCK, &mask, NULL, 8);
}


void IRQ::guardian(int signum) {
	/* Interrupts are prohibited during the ISR */
	irq.ast_level++;
    irq.m_gate[signum](signum);
	irq.ast_level--;
	if (irq.ast_level == 0 && irq.ast_requested) {
		irq.ast_requested = false;
		os::scheduler::ScheduleC_impl(0);
	}
}

IRQ arch::irq;
