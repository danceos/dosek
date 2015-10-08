#ifndef __OSEK_V_TIMER_H__
#define __OSEK_V_TIMER_H__

namespace arch {
  struct Timer {
	  static void init(unsigned interval_ms = 1);
	  static void reload();
	  static void tick();

	  static unsigned interval;
  };
}

#endif
