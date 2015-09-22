import os
from .config_tree import *
from .constraints import find_constraints, expr

constraints = find_constraints("*.py", basedir = os.path.abspath(os.path.dirname(__file__) + "/.."))

model = ConfigurationTree({
    'generator': OneOf(["make", "ninja", "eclipse"],
                       short_help = "Build System"),
    'arch': {
        "self" : OneOf(["i386", "ARM", "posix", "osek-v"],
                       short_help = "CPU Architecture"),
        'mpu': Boolean(short_help = "Use Memory Protection"),

        'idle-halt': Boolean(short_help = "Idle loop halts processor",
                             default_value = expr("self == i386 || self == ARM")),
        # config-constraint-: arch.idle-halt -> !(arch.self == posix)

        'privilege-isolation': Boolean(short_help = "Enable Priviledge isolation",
                                       default_value = expr("self == i386 || self == ARM")),
        # config-constraint-: arch.privilege-isolation -> (arch.self == i386 || arch.self == ARM)
        # config-constraint-: !arch.privilege-isolation -> (arch.self == i386 || arch.self == posix || arch.self == osek-v)
    },
    'os' : {
        'ignore-interrupt-systemcalls': Boolean(short_help = "Do not analyze DisableInterrupt() etc."),
        'passes': {
            'sse': Boolean(short_help = 'Enable SSE Analysis'),
        },
        'systemcalls': OneOf(["normal", "fsm", "fsm_pla", "wired"],
                              short_help = "System Call Implementation",),
        'specialize': Boolean(short_help = "Generate Specialized Systemcalls"),
        'inline-scheduler': Boolean(short_help = "Partial Scheduler", default_value = True),

        'basic-tasks': Boolean(short_help = "Should Basic Tasks be optimized?"),
        # config-constraint-: os.basic-tasks -> (arch.self == posix || arch.self == i386)
        # config-constraint-: os.basic-tasks -> !arch.mpu
    },
    'dependability' : {
        'encoded': Boolean(short_help = "Encoded OS Operations"),
        # config-constraint-: dependability.encoded -> (os.systemcalls == normal)
        'retry-scheduler': Boolean(short_help = "Retry Scheduler on Failure"),
        # config-constraint-: dependability.retry-scheduler -> dependability.encoded

        'state-replication': Boolean(short_help = "Save OS state multiple times"),
        # config-constraint-: dependability.state-replication -> (os.systemcalls == normal)

        'state-asserts': Boolean(short_help = "Introduce State Asserts into the system"),
        'cfg-regions': Boolean(short_help = "Introduce CFG Region Checks"),
        'failure-logging': Boolean(short_help = "Failure Logging"),
    },
    'app': {
        'name': String(short_help = "Name of one application"),
    }
})
