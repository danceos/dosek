#ifndef __OSEK_V_TIMER_H__
#define __OSEK_V_TIMER_H__

namespace arch {
  struct Timer {
	  static void init();
	  static void reload();
	  static void tick();
  };
}

#endif
