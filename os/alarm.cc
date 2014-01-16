#include "counter.h"
#include "alarm.h"

namespace os {

__attribute__((weak)) Alarm alarm0(counter0);

} // namespace os