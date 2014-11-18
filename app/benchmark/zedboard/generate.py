#!/usr/bin/python3

from optparse import OptionParser
import math

oil_template = """
CPU TestSystem {{

    OS TestSystem {{
        STATUS = STANDARD;
        ERRORHOOK = FALSE;
        STARTUPHOOK = FALSE;
        SHUTDOWNHOOK = FALSE;
        PRETASKHOOK = FALSE;
        POSTTASKHOOK = FALSE;
    }};

    RESOURCE RES_SCHEDULER {{
        RESOURCEPROPERTY = STANDARD;
    }};

    ISR reboot {{
       CATEGORY = 2;
       DEVICE = 5;
    }};

    ISR isrA {{
       CATEGORY = 2;
       DEVICE = 32;
    }};

    ISR isrB {{
        CATEGORY = 2;
        DEVICE = 33;
    }};

{fragments}

}};"""

oil_task_template = """
    TASK {name} {{
        SCHEDULE = {schedule};
        PRIORITY = {priority};
        ACTIVATION = 1;
        RESOURCE = RES_SCHEDULER;
        AUTOSTART = FALSE;
    }};
"""

oil_counter_template = """
    COUNTER {name} {{
        MAXALLOWEDVALUE = {maxallowedvalue};
        TICKSPERBASE = 1;
        MINCYCLE = 1;
        SOFTCOUNTER = {softcounter};
    }};
"""

oil_alarm_template = """
    ALARM {name} {{
        COUNTER = {counter};
        ACTION = ACTIVATETASK {{
            TASK = {task};
        }};
        AUTOSTART = TRUE {{
            ALARMTIME = {alarmtime};
            CYCLETIME = {cycletime};
        }};
    }};
"""




def pseudo_random(lower, upper, seed):
    lower = int(lower)
    upper = int(upper)
    # A few prime numbers
    factors = [
        353,   359,   367,   373,   379,   383,   389,
        2269,  2273,  2281,  2287,  2293,  2297,  2309,  2311,  2333,
        2339,  2341,  2347,  2351,  2357
    ]
    # We define an generator prime, that is used to multiply and divide
    generator_prime = 1217
    delta = upper - lower + 1
    seed = math.sqrt(
            abs(
                (seed * factors[int(seed) % len(factors)]) % 265359
            ))
    X = int(seed * generator_prime) % delta
    return lower + X

def pseudo_shuffle(lst, seed):
    ret = []
    # Copy the list structure
    lst = list(lst)
    while lst:
        seed = pseudo_random(0, 10000, seed)
        idx = pseudo_random(0, len(lst)-1, seed)
        ret.append(lst[idx])
        del lst[idx]
    return ret

class TaskPair:
    def __init__(self, options, idx):
        self.idx = idx
        # The higher priority tasks have a minimum static priority of
        self.task_low_priority = idx
        self.task_high_priority = options.size + 1000 + idx

        # What action should the task issue
        self.actions = {"low": [], "high": []}

        self.regenerate()

    def regenerate(self):
        self.oil_fragments = []
        self.generate_oil_tasks(self.idx)
        self.generate_oil_counters(self.idx)
        self.generate_oil_alarms(self.idx)


    def generate_oil_tasks(self, idx):
        # For every unit of the system, we generate:
        # - 2 tasks
        #   - 1 preemptable (high priority)
        #   - 1 unpreemptable (low priority)
        self.task_low_name = "T_%d_L" % (idx)
        task_low = oil_task_template.format(
            name = self.task_low_name,
            schedule = "NON",
            priority = self.task_low_priority
        )

        self.task_high_name = "T_%d_H" % (idx)
        task_high = oil_task_template.format(
            name = self.task_high_name,
            schedule = "FULL",
            priority = self.task_high_priority
        )
        self.oil_fragments += [task_high, task_low]

    def generate_oil_counters(self, idx):
        # The lower task is activated by an real counter, the high
        # priority task is activated by an soft counter
        self.real_counter_name = "C_%d_hard" % idx
        real_counter = oil_counter_template.format(
            name = self.real_counter_name,
            softcounter = "FALSE",
            maxallowedvalue = pseudo_random(40000, 50000, 5.5 * idx)
        )

        self.soft_counter_name = "C_%d_soft" % idx
        soft_counter = oil_counter_template.format(
            name = self.soft_counter_name,
            softcounter = "TRUE",
            maxallowedvalue = pseudo_random(40000, 50000, 3.7 * idx)
        )
        self.oil_fragments += [real_counter, soft_counter]

    def generate_oil_alarms(self, idx):
        # Each Counter is connected to an alarm. The hard counter does
        # activate the low priority task, the soft counter activates
        # the high priority task
        self.real_alarm_name = "A_%d_hard" % idx
        real_alarm = oil_alarm_template.format(
            name = self.real_alarm_name,
            counter = self.real_counter_name,
            task = self.task_low_name,
            cycletime = pseudo_random(3, 7,
                                      3.14 * idx),
            alarmtime = pseudo_random(1, 20,
                                      2.7 * idx)
        )
        self.soft_alarm_name = "A_%d_soft" % idx
        soft_alarm = oil_alarm_template.format(
            name = self.soft_alarm_name,
            counter = self.soft_counter_name,
            task = self.task_high_name,
            cycletime = pseudo_random(1, 4,
                                      4.123 * idx),
            alarmtime = pseudo_random(3, 7,
                                      1.33 * idx)
        )

        self.oil_fragments += [real_alarm, soft_alarm]


class TaskCoder:
    def __init__(self, task_pair, idx):
        self.idx = idx
        self.task_pair = task_pair

        self.definitions = []
        self.declarations = [
            "DeclareTask(%s);" % self.task_pair.task_low_name,
            "DeclareTask(%s);" % self.task_pair.task_high_name,
            "DeclareCounter(%s);" % self.task_pair.real_counter_name,
            "DeclareCounter(%s);" % self.task_pair.soft_counter_name,
            "DeclareAlarm(%s);" % self.task_pair.real_alarm_name,
            "DeclareAlarm(%s);" % self.task_pair.soft_alarm_name,
            ""
        ]

        self.generate_low_task()
        self.generate_high_task()

    def generate_low_task(self):
        post_hook = "/* Post Hook */"
        terminate = "TerminateTask();"

        # What actions are issued for this task?
        for action, arg in self.task_pair.actions["low"]:
            if action == "ChainTask":
                terminate = "ChainTask(%s);" % arg
            elif action == "ActivateTask":
                post_hook += "\n    ActivateTask(%s);" % arg
            else:
                assert False

        self.definitions.append("""
TASK({name}) {{
        int idx = ({idx} - 1) << 1 | 0;
        TickType data;
        IncrementCounter({softcounter});
        // kout << "LowTask {idx}" << endl;
        GetAlarm({realalarm}, &data);
        data = Calc(idx, data);
        Pulse(idx, data);
        {post_hook}
        {terminate}
}}
        """.format(name = self.task_pair.task_low_name,
                   idx = self.idx,
                   softcounter = self.task_pair.soft_counter_name,
                   realalarm = self.task_pair.real_alarm_name,
                   post_hook = post_hook,
                   terminate = terminate))

    def generate_high_task(self):
        pre_hook = "data = Calc(idx, ticks);"
        post_hook = "/* Post Hook */"
        terminate = "TerminateTask();"

        # What actions are issued for this task?
        for action, arg in self.task_pair.actions["high"]:
            if action == "ChainTask":
                terminate = "ChainTask(%s);" % arg
            elif action == "SetVar":
                post_hook += "\n\t%s = 0xaa;" % arg
            elif action == "WaitVar":
                pre_hook += "\n\twhile({var} != 0xaa) {{ data = Calc(idx, ticks); }}; {var} = 00;"\
                    .format(idx = self.idx, var = arg)
            else:
                assert False

        self.definitions.append("""
TASK({name}) {{
        uint32_t idx = ({idx} - 1) << 1 | 1;
        uint32_t data;
        TickType ticks;
        GetAlarm({softalarm}, &ticks);

        {pre_hook}

        GetResource(RES_SCHEDULER);
        Pulse(idx, data);
        ReleaseResource(RES_SCHEDULER);

        {post_hook}
        {terminate}
}}
        """.format(name = self.task_pair.task_high_name,
                   idx = self.idx,
                   softalarm = self.task_pair.soft_alarm_name,
                   pre_hook = pre_hook,
                   post_hook = post_hook,
                   terminate = terminate))




def generate_system(options):
    task_pairs = {}
    task_coders = {}
    oil_fragments = []
    c_declarations = []
    c_defintions = []

    for idx in range(1, options.size + 1):
        task_pairs[idx] = TaskPair(options, idx)

    # Number of tasks
    c_declarations.append( """
const uint16_t number_of_tasks = {tasks};
uint16_t pulse_counter_by_task[{tasks}];"""\
                           .format(tasks = len(task_pairs) * 2))

    # Connect one third of all task pairs
    random_pairs = pseudo_shuffle(task_pairs.values(),
                                  len(task_pairs) / 5)
    statistics = {"ChainTask_from_low": 0,
                  "ActivateTask_from_low": 0,
                  "ChainTask_from_high": 0,
                  "SetVar_from_high": 0
                  }
    for idx in range(0, len(random_pairs), 3):
        # We have identified a source and a target task pair
        source = random_pairs[idx]
        target = (random_pairs + random_pairs)[idx + 1]
        # We dice wheter the low task or the high task exposes the "signal"
        low_does_expose = pseudo_shuffle([False, True], source.task_high_priority)[0]
        if low_does_expose:
            if source.task_low_priority < target.task_low_priority:
                # We chain to the targets high priority task. At this
                # point we now, we are the lowest priority task among
                # the four involved tasks.
                source.actions["low"].append( ('ChainTask', target.task_high_name) )
                statistics["ChainTask_from_low"] += 1
            else:
                # Activate the lowest prior Task. This lead to an
                # activated but, not running task
                source.actions["low"].append( ('ActivateTask', target.task_low_name) )
                statistics["ActivateTask_from_low"] += 1
        else:
            if source.task_high_priority < target.task_high_priority:
                # We have a lower priority. Therefore we chain to the higher prior task
                source.actions["high"].append( ('ChainTask', target.task_high_name) )
                statistics["ChainTask_from_high"] += 1
            else:
                # We let the higher prior task set an variable, the
                # lower prior high task does wait for
                assert source.task_low_priority < target.task_high_priority
                # Switch the external activated task priority of the
                # higher pair with the lowers high task.

                # ATTENTION! This avoids dead locks
                source.task_low_priority, target.task_high_priority \
                    = target.task_high_priority, source.task_low_priority
                source.regenerate()
                target.regenerate()

                var_name = "comm_%d_to_%d" % ( source.idx, target.idx )
                c_declarations.append("static volatile int %s;" % var_name)
                source.actions["high"].append( ('SetVar', var_name) )
                target.actions["high"].append( ('WaitVar', var_name) )

                statistics["SetVar_from_high"] += 1

    print(statistics)

    for idx in range(1, options.size + 1):
        oil_fragments += ["\n   /* TaskPair %d */\n" % idx]
        oil_fragments += task_pairs[idx].oil_fragments

        task_coders[idx] = TaskCoder(task_pairs[idx], idx)
        c_declarations += task_coders[idx].declarations
        c_defintions += task_coders[idx].definitions


    # Write OIL file
    oil = oil_template.format(
        fragments    = "".join(oil_fragments),
    )
    with open(options.oil, "w+") as fd:
        fd.write(oil)

    # C Code
    c_code = "\n".join(c_declarations + c_defintions)
    with open(options.dosek, "w+") as fd:
        fd.write(c_code + "\n")

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--dosek", dest="dosek",
                      help="dosek.cc path", metavar="FILE",
                      default="./dosek-tasks.cc")

    parser.add_option("-o", "--oil", dest="oil",
                      help="system.oil path", metavar="FILE",
                      default="./system.oil")
    parser.add_option("-s", "--size", dest="size",
                      help="size of the system", metavar="SIZE",
                      default = 1)

    (options, args) = parser.parse_args()
    options.size = int(options.size)

    generate_system(options)
