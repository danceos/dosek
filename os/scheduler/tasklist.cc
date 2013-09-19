#include "tasklist.h"

extern "C" {

constexpr Encoded_Static<A0, 13> TaskList::idle_id;
constexpr Encoded_Static<A0, 12> TaskList::idle_prio;
Encoded_Static<A0, 3> TaskList::id;
Encoded_Static<A0, 2> TaskList::prio;

};
