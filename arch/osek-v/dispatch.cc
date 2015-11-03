#include "dispatch.h"

#ifndef CONFIG_OS_SYSTEMCALLS_WIRED

static char __attribute__(( aligned (16) )) idlestack[arch::IDLESTACKSIZE];
arch::TCB::dynamic_state idle_dynamic_state;
arch::TCB arch::Dispatcher::m_idle(Dispatcher::idleEntry, idlestack, idle_dynamic_state, arch::IDLESTACKSIZE);
const arch::TCB* arch::Dispatcher::m_current = 0;

#endif
