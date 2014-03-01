from generator.rules.unencoded import UnencodedSystem, TaskListTemplate, \
    SchedulerTemplate
from generator.elements import VariableDefinition, Statement

class EncodedSystem(UnencodedSystem):
    def __init__(self):
        UnencodedSystem.__init__(self)
        self.task_list = EncodedTaskListTemplate
        self.scheduler = EncodedSchedulerTemplate

    def sigs(self, count):
        Bs = [str(self.generator.signature_generator.new()) for _ in range(0, count)]
        return "<%s>" %(", ".join(Bs))

    def generate_system_code(self):
        # The current_prio_sig has to be allocated before the tasklist
        # is instanciated. Otherwise a TAssert in tasklist.h fails
        self.objects["Scheduler"] = {}
        self.objects["Scheduler"]["scheduler_prio_sig"] = self.generator.signature_generator.new()
        self.objects["Scheduler"]["current_prio_sig"] = self.generator.signature_generator.new()
        self.objects["Scheduler"]["current_task_sig"] = self.generator.signature_generator.new()

        UnencodedSystem.generate_system_code(self)

    def convert_argument(self, block, argument):
        b = self.generator.signature_generator.new()
        var = VariableDefinition.new(self.generator, "Encoded_Static<A0, %d>" % b)
        block.prepend(var)
        block.add(Statement("%s.encode(%s)" % (var.name, argument[0])))
        return var


class EncodedTaskListTemplate(TaskListTemplate):
    def __init__(self, rules):
        TaskListTemplate.__init__(self, rules)

        self.__head_signature_vc = self.generator.signature_generator.new()
        # Generate signatures for each task for prio and id
        for subtask in self.system_graph.get_subtasks():
            self.objects[subtask]["task_id_sig"] = self.generator.signature_generator.new()
            self.objects[subtask]["task_prio_sig"] = self.generator.signature_generator.new()

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
            last_sig = self.__head_signature_vc
            next_sig = self.generator.signature_generator.new()
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
        self.__head_signature_vc = self.generator.signature_generator.new()
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

