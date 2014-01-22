#include "dispatch.h"

static char idlestack[arch::IDLESTACKSIZE];
static void * idle_sp;
arch::TCB arch::Dispatcher::m_idle(Dispatcher::idleEntry, idlestack, idle_sp, arch::IDLESTACKSIZE);
const arch::TCB* arch::Dispatcher::m_current = 0;

 
extern "C" void kickoff() {
	arch::Dispatcher::getCurrent()->set_running();
	Machine::enable_interrupts();
	arch::Dispatcher::getCurrent()->fun();
}

