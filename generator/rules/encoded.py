from generator.rules.base import BaseRules
from generator.elements import CodeTemplate, Include

class EncodedSystem(BaseRules):
    def __init__(self):
        BaseRules.__init__(self)

    def generate_system_code(self):
        self.generator.source_file.includes.add(Include("os/scheduler/tasklist.h"))
        task_list = TaskListTemplate(self)
        self.generator.source_file.declarations.append(task_list.expand())

class TaskListTemplate(CodeTemplate):
    def __init__(self, rules):
        CodeTemplate.__init__(self, rules.generator, "os/scheduler/tasklist.h.in")
        self.rules = rules
        self.system_graph = self.generator.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.rules.objects
        self.idle = self.system_graph.find_function("Idle")

        self.__head_signature_vc = self.generator.signature_generator.new()
        # Generate signatures for each task for prio and id
        for subtask in self.system_graph.get_subtasks():
            self.objects[subtask]["task_id_sig"] = self.generator.signature_generator.new()
            self.objects[subtask]["task_prio_sig"] = self.generator.signature_generator.new()

    def arbitrary_new_signature(self, snippet, args):
        return str(self.generator.signature_generator.new())

    def __foreach_task(self, func):
        """Call func for every subtask, that is a real task and collect the
        results in a list."""
        ret = []
        for subtask in self.system_graph.get_subtasks():
            if not subtask in self.objects:
                self.objects[subtask] = {}
            # Ignore the Idle thread and ISR subtasks
            if not subtask.is_real_thread():
                continue
            ret += func(subtask)
        return ret

    def ready_flag_variables(self, snippet, args):
        def do(subtask):
            # Intantiate the correct macros
            return self.expand_snippet("ready_flag",
                                       name = subtask.name,
                                       A = "A0",
                                       B = self.objects[subtask]["task_prio_sig"]) + "\n"

        return self.__foreach_task(do)

    def ready_flag_constructor(self, snippet, args):
        def do(subtask):
            return self.expand_snippet("ready_flag_init", name = subtask.name)

        return self.__foreach_task(do)

    def task_set_call(self, snippet, args):
        def do(subtask):
            return self.expand_snippet("task_set_entry", 
                                       name = subtask.name,
                                       id = self.objects[subtask]["task_id"])

        return self.__foreach_task(do)

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
            return self.expand_snippet("head_update_max",
                                       task = subtask.name,
                                       last_sig = last_sig,
                                       next_sig = next_sig,
                                       task_id  = self.objects[subtask]["task_id"],
                                       task_id_sig = self.objects[subtask]["task_id_sig"],
                                       signature = "0xAA")
        return self.__foreach_task(do)
