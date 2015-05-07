from .os_unencoded import UnencodedOS, TaskListTemplate, \
    SchedulerTemplate
from .elements import *
from generator.analysis.Resource import Resource
from .implementations import *

class SignatureGenerator:
    def __init__(self, number_of_tasks, start = 10000):
        self.sig = start
        self.number_of_tasks = number_of_tasks
        self.used = set()

        self.sigPos = 3
        self.scheduler_prio   = 12
        self.current_prio = 11
        self.current_task = 10
        self.minimum_task_prio = (self.sigPos * (self.number_of_tasks + 1)) \
                                 + self.scheduler_prio

    def new(self):
        i = 1
        while (self.sig + i) in self.used:
            i += 1
        x = self.sig + i
        self.sig = x
        self.used.add(x)
        return x

    def new_task_id(self):
        return self.morethan(self.minimum_task_prio)

    def lessthan(self, other):
        i = 1
        while (other - i) in self.used:
            i += 1
        x = other - i
        assert x > 0
        self.used.add(x)
        return x
    def morethan(self, other):
        i = 1
        while (other + i) in self.used:
            i += 1
        x = other + i
        assert x > 0
        self.used.add(x)
        return x


class EncodedOS(UnencodedOS):
    def __init__(self):
        super(EncodedOS, self).__init__()
        self.task_list = EncodedTaskListTemplate
        self.scheduler = EncodedSchedulerTemplate
        self.counter_signatures = {}

    def generate_system_code(self):
        # The current_prio_sig has to be allocated before the tasklist
        # is instanciated. Otherwise a TAssert in tasklist.h fails
        self.sigs = self.generator.signature_generator

        impl = EncodedSchedulerImpl()
        self.system_graph.impl.scheduler = impl
        impl.scheduler_prio_sig = self.sigs.scheduler_prio
        impl.current_prio_sig = self.sigs.current_prio
        impl.current_task_sig = self.sigs.current_task

        super(EncodedOS, self).generate_system_code()

    def convert_argument(self, block, argument):
        b = self.generator.signature_generator.new()
        var = VariableDefinition.new(self.generator, "Encoded_Static<A0, %d>" % b)
        block.prepend(var)
        block.add(Statement("%s.encode(%s)" % (var.name, argument[0])))
        return var

    def generate_counter(self, ctr):
        signature = self.generator.signature_generator.new()
        counter = DataObject("EncodedCounter<%d>" % signature,
                             "OS_%s_counter" % (ctr.name),
                             "(%d, %d, %d)" % (ctr.conf.maxallowedvalue,
                                               ctr.conf.ticksperbase,
                                               ctr.conf.mincycle))
        self.counter_signatures[ctr.conf.name] = signature
        return counter

    def generate_alarm(self, alarm, counter, task):
        signature = self.generator.signature_generator.new()
        alarm = DataObject("EncodedAlarm<%d, %d, &%s>" % (signature, self.counter_signatures[counter.name],
                                                          counter.impl.name),
                           "OS_%s_alarm" %( alarm.conf.name),
                           "(%s, %s, %d, %d, %d)" % (task,
                                                     str(alarm.conf.armed).lower(),
                                                     alarm.conf.reltime,
                                                     alarm.conf.cycletime,
                                                     alarm.impl.alarm_id))
        return alarm

    def get_syscall_return_variable(self, Type, size = 2):
        """Returns a Variable, that is able to capture the return value of a
           system call. The self.return_variables dict is defined in the super class.

        """
        if Type in self.return_variables:
            return self.return_variables[Type]

        if size == 2:
            var = DataObject("os::redundant::WithLinkage<uint32_t, os::redundant::MergedDMR>",
                             "syscall_return_%s" % Type)
        elif size == 4:
            var = DataObject("os::redundant::DMRWithLinkage<%s>" % Type, 
                             "syscall_return_%s" % Type)
        else:
            assert False, (Type, size, "Invalid Syscall Return Variable")

        self.generator.source_file.data_manager.add(var)
        self.return_variables[Type] = var
        return var

class EncodedTaskListTemplate(TaskListTemplate):
    def __init__(self, rules):
        TaskListTemplate.__init__(self, rules)

        self.__head_signature_vc = self.generator.signature_generator.new()
        # Generate signatures for each task for prio and id
        for subtask in self.system_graph.user_subtasks:
            sig = self.generator.signature_generator.new_task_id()
            subtask.impl.task_id_sig = sig
            subtask.impl.task_prio_sig = sig

        if self.generator.conf.dependability.retry_scheduler:
            self.snippets['head_fail'] = self.snippets['head_fail_retry']
        else:
            self.snippets['head_fail'] = self.snippets['head_fail_fail']

    def template_file(self):
        return "os/scheduler/tasklist.h.in"

    def subtask_prio_sig(self, snippet, args):
        return str(self._subtask.impl.task_prio_sig)

    def subtask_id_sig(self, snippet, args):
        return str(self._subtask.impl.task_id_sig)

    def idle_id_sig(self, snippet, args):
        return str(self.idle.impl.task_id_sig)

    def idle_prio_sig(self, snippet, args):
        return str(self.idle.impl.task_prio_sig)

    def scheduler_prio(self, snippet, args):
        RES_SCHEDULER = self.system_graph.get(Resource, "RES_SCHEDULER")
        return str(RES_SCHEDULER.conf.static_priority)

    def scheduler_prio_sig(self, snippet, args):
        return str(self.system_graph.impl.scheduler.scheduler_prio_sig)

    # events
    def foreach_event(self, snippet, args):
        body = args[0]
        ret = ""
        for event in self._subtask.events:
            self._event = event
            ret += self.expand_snippet(body)
        return ret

    def event(self, snippet, args):
        return self._event.name

    def event_mask(self, snippet, args):
        return str(self._event.event_mask)

    def event_list(self, snippet, args):
        return ", ".join([x.name for x in self._subtask.events])

    # head()
    def if_comp_idx_gt_zero(self, snippet, args):
        if self.comp_idx > 0:
            return self.expand_snippet(args[0])
        return ""

    def if_comp_idx_eq_zero(self, snippet, args):
        if self.comp_idx == 0:
            return self.expand_snippet(args[0])
        return ""

    def head_update_max_cascade(self, snippet, args):
        """Generate the update max cascade for tasklist::head"""
        self.comp_idx = 0
        def do(subtask):
            self._subtask = subtask
            # Generate a new signature for this cascade step
            x = self.expand_snippet("head_update_max")
            self.comp_idx += 1
            return x
        ret = self.rules.foreach_subtask(do)

        return ret

    def prio_offset(self, snippet, args):
        RES_SCHEDULER = self.system_graph.get(Resource, "RES_SCHEDULER")
        return str(RES_SCHEDULER.conf.static_priority + 1)


class EncodedSchedulerTemplate(SchedulerTemplate):
    def template_file(self):
        return "os/scheduler/scheduler.h.in"

    def arbitrary_new_signature(self, snippet, args):
        return str(self.generator.signature_generator.new())

    def current_task_sig(self, snippet, args):
        return str(self.system_graph.impl.scheduler.current_task_sig)
    def current_prio_sig(self, snippet, args):
        return str(self.system_graph.impl.scheduler.current_prio_sig)

