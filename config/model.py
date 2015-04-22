{
    'generator': OneOf(["make", "ninja", "eclipse"],
                       short_help = "Build System"),
    'arch': {
        "self" : OneOf(["i386", "ARM", "posix"],
                       short_help = "CPU Architecture"),
        'mpu': Boolean(short_help = "Use Memory Protection"),
    },
    'os' : {
        'passes': {
            'sse': Boolean(short_help = 'Enable SSE Analysis'),
        },
        'specialize': Boolean(short_help = "Generate Specialized Systemcalls"),
    },
    'dependability' : {
        'encoded': Boolean(short_help = "Encoded OS Operations"),
        'state-asserts': Boolean(short_help = "Introduce State Asserts into the system"),
        'cfg-regions': Boolean(short_help = "Introduce CFG Region Checks"),
        'failure-logging': Boolean(short_help = "Failure Logging"),
    },
}
