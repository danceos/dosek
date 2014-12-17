from generator.rules.unencoded import UnencodedSystem, TaskListTemplate, \
    SchedulerTemplate
from generator.elements import *

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


class EncodedSystem(UnencodedSystem):
    def __init__(self):
        UnencodedSystem.__init__(self)
        self.task_list = EncodedTaskListTemplate
        self.scheduler = EncodedSchedulerTemplate
        self.counter_signatures = {}

    def generate_system_code(self):
        # The current_prio_sig has to be allocated before the tasklist
        # is instanciated. Otherwise a TAssert in tasklist.h fails
        self.sigs = self.generator.signature_generator
        self.objects["Scheduler"] = {}
        self.objects["Scheduler"]["scheduler_prio_sig"] = self.sigs.scheduler_prio
        self.objects["Scheduler"]["current_prio_sig"] = self.sigs.current_prio
        self.objects["Scheduler"]["current_task_sig"] = self.sigs.current_task

        UnencodedSystem.generate_system_code(self)

    def convert_argument(self, block, argument):
        b = self.generator.signature_generator.new()
        var = VariableDefinition.new(self.generator, "Encoded_Static<A0, %d>" % b)
        block.prepend(var)
        block.add(Statement("%s.encode(%s)" % (var.name, argument[0])))
        return var

    def generate_counter(self, counter_info):
        signature = self.generator.signature_generator.new()
        counter = DataObject("EncodedCounter<%d>" % signature,
                             "OS_%s_counter" % (counter_info.name),
                             "(%d, %d, %d)" % (counter_info.maxallowedvalue,
                                               counter_info.ticksperbase,
                                               counter_info.mincycle))
        self.counter_signatures[counter.name] = signature
        return counter

    def generate_alarm(self, alarm_info, counter, task):
        signature = self.generator.signature_generator.new()
        alarm = DataObject("EncodedAlarm<%d, %d, &%s>" % (signature, self.counter_signatures[counter], counter),
                           "OS_%s_alarm" %( alarm_info.name),
                           "(%s, %s, %d, %d)" % (task,
                                                     str(alarm_info.initial_armed).lower(),
                                                     alarm_info.initial_reltime,
                                                     alarm_info.initial_cycletime))
        return alarm

    def get_syscall_return_variable(self, Type):
        """Returns a Variable, that is able to capture the return value of a
           system call. The self.return_variables dict is defined in the super class.

        """
        if Type in self.return_variables:
            return self.return_variables[Type]

        var = DataObject("os::redundant::WithLinkage<uint32_t, os::redundant::MergedDMR>",
                         "syscall_return_%s" % Type)
        self.generator.source_file.data_manager.add(var)
        self.return_variables[Type] = var
        return var

class EncodedTaskListTemplate(TaskListTemplate):
    def __init__(self, rules):
        TaskListTemplate.__init__(self, rules)

        self.__head_signature_vc = self.generator.signature_generator.new()
        # Generate signatures for each task for prio and id
        for subtask in self.system_graph.get_subtasks():
            # ISR do not need an signature
            if subtask.is_isr:
                continue
            sig = self.generator.signature_generator.new_task_id()
            self.objects[subtask]["task_id_sig"] = sig
            self.objects[subtask]["task_prio_sig"] = sig

    def template_file(self):
        return "os/scheduler/tasklist.h.in"

    def arbitrary_new_signature(self, snippet, args):
        return str(self.generator.signature_generator.new())


    def ready_flag_variables(self, snippet, args):
        def do(subtask):
            # Intantiate the correct macros
            return self.expand_snippet("ready_flag",
                                       name = subtask.name,
                                       A = "A0",
                                       B = self.objects[subtask]["task_prio_sig"]) + "\n"

        return self.foreach_subtask(do)

    def task_set_call(self, snippet, args):
        def do(subtask):
            return self.expand_snippet(args[0],
                                       name = subtask.name,
                                       id = self.objects[subtask]["task_id"])

        return self.foreach_subtask(do)

    def idle_id_sig(self, snippet, args):
        return str(self.objects[self.idle]["task_id_sig"])

    def idle_prio_sig(self, snippet, args):
        return str(self.objects[self.idle]["task_prio_sig"])


    # Implementation of head
    def head_signature_vc(self, snippet, args):
        """Returns the current chaining signature, used in
        TaskList::head. This initialised in __init__ and updated in
        head_update_max_cascade."""
        return str(self.__head_signature_vc)

    def head_update_max_cascade(self, snippet, args):
        """Generate the update max cascade for tasklist::head"""
        def do(subtask):
            # Generate a new signature for this cascade step
            last_sig = 3 #self.__head_signature_vc
            next_sig = 3  #self.generator.signature_generator.new() % 71
            self.__head_signature_vc = next_sig
            do.i += 1
            return self.expand_snippet("head_update_max",
                                       task = subtask.name,
                                       last_sig = last_sig,
                                       next_sig = next_sig,
                                       task_id  = self.objects[subtask]["task_id"],
                                       task_id_sig = self.objects[subtask]["task_id_sig"],
                                       i = str(do.i-1),
                                       ii = str(do.i)
                                       )
        # This is a ugly hack to fix python binding madness
        do.i = 0
        ret = self.foreach_subtask(do)

        # Update current prio for idle task
        last_sig = self.__head_signature_vc
        self.__head_signature_vc = 3
        ret += self.expand_snippet("head_update_idle_prio",
                                   last_sig = last_sig,
                                   next_sig = self.__head_signature_vc,
                                   i = str(do.i), ii = str(do.i + 1))

        return ret



class EncodedSchedulerTemplate(SchedulerTemplate):
    def template_file(self):
        return "os/scheduler/scheduler.h.in"

    def arbitrary_new_signature(self, snippet, args):
        return str(self.generator.signature_generator.new())

    def current_task_sig(self, snippet, args):
        return str(self.objects["Scheduler"]["current_task_sig"])
    def current_prio_sig(self, snippet, args):
        return str(self.objects["Scheduler"]["current_prio_sig"])
    def scheduler_prio_sig(self, snippet, args):
        return str(self.objects["Scheduler"]["scheduler_prio_sig"])

    def scheduler_prio(self, snippet, args):
        return str(self.system_graph.scheduler_priority())

    # Reschedule
    def activate_task_foreach_task(self, snippet, args):
        def do(subtask):
            id_sig = self.generator.signature_generator.lessthan(self.objects[subtask]["task_prio_sig"])
            prio_sig = self.generator.signature_generator.lessthan(self.objects[subtask]["task_prio_sig"])
            return self.expand_snippet("activate_task_task",
                                       task = self.objects[subtask]["task_descriptor"].name,
                                       id_sig = str(id_sig),
                                       prio_sig = str(prio_sig),
                                       task_prio_sig = self.objects[subtask]["task_prio_sig"],
                                       )

        return self.foreach_subtask(do)

