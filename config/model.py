import os
from .config_tree import *
from .constraints import find_constraints

constraints = find_constraints("*.py", basedir = os.path.abspath(os.path.dirname(__file__) + "/.."))

model = ConfigurationTree({
    'generator': OneOf(["make", "ninja", "eclipse"],
                       short_help = "Build System"),
    'arch': {
        "self" : OneOf(["i386", "ARM", "posix"],
                       short_help = "CPU Architecture"),
        'mpu': Boolean(short_help = "Use Memory Protection"),
    },
    'os' : {
        'ignore-interrupt-systemcalls': Boolean(short_help = "Do not analyze DisableInterrupt() etc."),
        'passes': {
            'sse': Boolean(short_help = 'Enable SSE Analysis'),
        },
        'systemcalls': OneOf(["normal", "fsm", "fsm_pla"],
                              short_help = "System Call Implementation",),
        'specialize': Boolean(short_help = "Generate Specialized Systemcalls"),

        'basic-tasks': Boolean(short_help = "Should Basic Tasks be optimized?"),
        # config-constraint-: os.basic-tasks -> (arch.self == posix)
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
