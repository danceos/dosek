#ifndef CONTEXT_MANAGER_H
#define CONTEXT_MANAGER_H

#include "ucontextimpl.h"
#include <map>

namespace arch {

class ContextManager {
    typedef std::map<os::scheduler::Task::id_t, arch::PosixContext> ctxmap_t;
    ctxmap_t map;

public:

    arch::PosixContext & getContext(int id) {
        return map[id];
    }


    arch::PosixContext & getContext(const os::scheduler::Task task) {
        return map[task.id];
    }

};


}; //end of namespace


#endif
