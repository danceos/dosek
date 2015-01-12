import os
import sys

class CheckedObject:
    """Manages a CheckedObject and its corresponding data"""

    typenumber = 0

    def __init__(self, name, size):
        self.size = size
        self.name = name
        self.typenumber = CheckedObject.typenumber
        CheckedObject.typenumber += 1

    def expand_declaration(self):
        return "DeclareCheckedObject(benchtype" + str(self.typenumber) \
            + ", %s);\n" % self.name

    def expand_typedef(self):
        return "typedef char benchtype" + str(self.typenumber) \
            + "[" + str(self.size) + "];\n"

    def expand_xml(self):
        return '''    CHECKEDOBJECT {name} {{
        HEADER = "app/bcc1/depbench/benchtype.h";
        TYPEDEF = benchtype{typenumber};
    }};
'''.format(name=self.name,
             typenumber=self.typenumber)


class BusyWaiting:
    """Manages a busy waiting loop"""

    def __init__(self, duration):
        self.duration = duration

    def dur(self):
        return self.duration

    def expand(self):
        return '''
    for (volatile unsigned int i = 0; i < %s; ++i) {
        // Avoid optimization
        asm volatile("" ::: "memory");
    }
''' % str(self.duration)


class Acquiration:
    """Manages an acquiration of an checkedObject"""

    def __init__(self, checkedObject, duration):
        self.checkedObject = checkedObject
        self.loop = BusyWaiting(duration)

    def dur(self):
        return self.loop.duration

    def expand(self):
        name = self.checkedObject.name
        return "    AcquireCheckedObject(" + name + ");" + self.loop.expand() \
            + "    ReleaseCheckedObject(" + name + ");\n"


class Benchfile:
    """Manages elements of an application file of a benchmark"""

    def __init__(self, repetitions):
        self.repetitions = repetitions
        self.sequence = []

    def add(self, part):
        self.sequence.append(part)

    def get_checkedObjects(self):
        co = []
        for e in self.sequence:
            if isinstance(e, Acquiration) and not e.checkedObject in co:
                co.append(e.checkedObject)
        return co

    def expand_file(self):
        content = '''
#include "os.h"
#include "dependability/depsvc.h"
#include "arch/generic/hardware_threads.h"
#include "dependability/dependability_service.h"
#include "output.h"
#include "benchtype.h"

DeclareTask(BenchTask);
'''
        for co in self.get_checkedObjects():
            content += co.expand_declaration()
        content += '''
// Dependability Service Startup
const unsigned int stacksize = 4096;
char dependability_stack[stacksize];

void os_main()
{
    arch::start_hardware_thread(1, dependability_stack, stacksize, dep::dependability_service);
    StartOS(0);
}

TASK(BenchTask) {
    for (unsigned int i = 0; i < ''' + str(self.repetitions) + '''; ++i) {
    static unsigned int finished = 0;
'''
        for e in self.sequence:
            content += e.expand()
        content += '''
    } // for
    kout << GET_DEPENDABILITY_FAILURE_COUNT() << "/" << GET_DEPENDABILITY_CHECK_COUNT() << endl;
    ShutdownMachine();
    TerminateTask();
}

PreIdleHook() {
    dep::release_all_CheckedObjects();
}'''
        return content

    def expand_type_header(self):
        content = '''
#ifndef BENCHTYPE_H_
#define BENCHTYPE_H_

'''
        for co in self.get_checkedObjects():
            content += co.expand_typedef()
        content += '''
#endif'''
        return content

    def expand_osekossystem(self):
        content = """CPU TestSystem {

    OS TestSystem {
        STATUS = STANDARD;
        ERRORHOOK = FALSE;
        STARTUPHOOK = FALSE;
        SHUTDOWNHOOK = FALSE;
        PRETASKHOOK = FALSE;
        POSTTASKHOOK = FALSE;
    };

    TASK BenchTask {
        TYPE = BASIC;
        SCHEDULE = FULL;
        PRIORITY = 4;
        ACTIVATION = 1;
        AUTOSTART = TRUE;
    };
"""
        for co in self.get_checkedObjects():
            content += co.expand_xml()

        content += "\n};"
        return content

    def generate_bench_app(self):
        reporoot = os.path.dirname(os.path.abspath(__file__)) + "/../../"
        approot = reporoot + "app/bcc1/depbench"
        try:
            os.mkdir(approot)
        except:
            pass
        approot += "/"
        cmakelists = open(approot + 'CMakeLists.txt', 'w')
        cmakelists.write('''DOSEK_BINARY (
  NAME bcc1_depbench
  depbench.cc
  SYSTEM_DESC system.oil
  LIBS libdepsvc
)''')
        cmakelists.close()
        depbench = open(approot + 'depbench.cc', 'w')
        depbench.write(self.expand_file())
        depbench.close()

        osekossystem = open(approot + 'system.oil', 'w')
        osekossystem.write(self.expand_osekossystem())
        osekossystem.close()

        benchtype = open(approot + 'benchtype.h', 'w')
        benchtype.write(self.expand_type_header())
        benchtype.close()

