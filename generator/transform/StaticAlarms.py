# coding: utf-8

from generator.analysis.Analysis import Analysis
from generator.analysis.AtomicBasicBlock import E, S
from generator.coder.elements import DataObject, Include
from collections import namedtuple
from fractions import gcd
import logging

class StaticAlarms(Analysis):
    """Checks all configured alarms in the system to be static. A static
       is a alarm, that is configured only statically and runs all
       the. (No CancelAlarm, SetRelAlarm)

    """

    pass_alias = "static-alarms"

    AlarmConfiguration = namedtuple("AlarmConfiguration", ["reltime", "cycletime"])

    def requires(self):
        return ["llvmpy"]

    def do(self):
        # By default all alarms are static
        static_counters = {x: True for x in self.system_graph.counters}
        static_alarms   = {x: True for x in self.system_graph.alarms}

        for abb in self.system_graph.abbs:
            # All manipulated alarms and counters are non-static
            if abb.isA([S.SetRelAlarm, S.CancelAlarm]):
                static_alarms[abb.arguments[0]] = False
            if abb.isA([S.AdvanceCounter]):
                static_counters[abb.arguments[0]] = False

        # An alarm can't be static, if the counter isn't static
        for alarm in static_alarms:
            if not static_counters[alarm.conf.counter]:
                static_alarms[alarm] = False

        # Only the static alarms
        static_alarms = [k for k,v in static_alarms.items() if v]

        base_period = None
        self.useless_alarms = set()
        for alarm in static_alarms:
            if not alarm.conf.armed:
                self.useless_alarms.add(alarm)
                logging.info("  Remove Alarm %s, since is not armed and no syscall references it",
                             alarm.conf.name)
                continue
            if not base_period:
                base_period = alarm.conf.reltime
            base_period = gcd(base_period, alarm.conf.reltime)
            base_period = gcd(base_period, alarm.conf.cycletime)
            logging.info("  Static Alarm: %s (t0 + %d + n × %d)", alarm.conf.name, alarm.conf.reltime, alarm.conf.cycletime)

        self.base_period = base_period
        self.static_alarms = {}
        for alarm in static_alarms:
            if not alarm.conf.armed:
                continue
            self.static_alarms[alarm] = self.AlarmConfiguration(
                reltime = alarm.conf.reltime//self.base_period,
                cycletime = alarm.conf.cycletime//self.base_period,
            )

    # Accessors for the analysis results
    def is_static(self, alarm):
        return alarm in self.static_alarms

    def is_useless(self, alarm):
        return alarm in self.useless_alarms
