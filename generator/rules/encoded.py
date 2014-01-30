from generator.rules.simple import SimpleSystem
from generator.elements import CodeTemplate, Include, Function

class EncodedSystem(SimpleSystem):
    def __init__(self):
        SimpleSystem.__init__(self)

    def enc_id(self, subtask):
        """Returns a string that generates an encoded id"""
        B = self.generator.signature_generator.new()
        task_desc = self.objects[subtask]["task_descriptor"].name
        ret = "%s.enc_id<%d>()" % (task_desc, B)
        return ret

    def generate_system_code(self):
        # The current_prio_sig has to be allocated before the tasklist
        # is instanciated. Otherwise a TAssert in tasklist.h fails
        self.objects["Scheduler"] = {}
        self.objects["Scheduler"]["current_prio_sig"] = self.generator.signature_generator.new()
        self.objects["Scheduler"]["current_task_sig"] = self.generator.signature_generator.new()

        self.generator.source_file.includes.add(Include("os/scheduler/tasklist.h"))
        task_list = TaskListTemplate(self)
        self.generator.source_file.declarations.append(task_list.expand())

        self.generator.source_file.includes.add(Include("os/scheduler/scheduler.h"))
        self.generator.source_file.includes.add(Include("os/scheduler/task.h"))
        scheduler = SchedulerTemplate(self)
        self.generator.source_file.declarations.append(scheduler.expand())

        self.generator.source_file.includes.add(Include("os/alarm.h"))
        alarms = AlarmTemplate(self)
        self.generator.source_file.declarations.append(alarms.expand())

    def StartOS(self, block):
        highestTask = None
        for subtask in self.system_graph.get_subtasks():
            if not subtask.autostart or not subtask.is_real_thread():
                continue
            if not highestTask or subtask.static_priority > highestTask.static_priority:
                highestTask = subtask
            self.call_function(block,
                               "SetReady_impl",
                               "void",
                               [self.objects[subtask]["task_descriptor"].name])

        if highestTask:
            self.call_function(block, "ActivateTaskC_impl", "void",
                               [self.enc_id(highestTask)])
        else:
            #FIXME: Dispatch to the idle loop
            self.call_function(block, "assert", "void", ["0"])

        self.call_function(block, "Machine::enable_interrupts", "void", [])
        self.call_function(block, "Machine::unreachable", "void", [])


    def TerminateTask(self, block, abb):
        self.call_function(block, "scheduler.TerminateTask_impl", "void",
                           [])

    def ActivateTask(self, block, abb):
        self.call_function(block,
                           "scheduler.ActivateTask_impl",
                           "void",
                           [self.enc_id(abb.arguments[0])])

    def ChainTask(self, block, abb):
        self.call_function(block,
                           "scheduler.ChainTask_impl",
                           "void",
                           [self.enc_id(abb.arguments[0])])


    def systemcall(self, systemcall, function):
        """Generate systemcall into function"""
        self.system_enter_hook(function)

        # Generate a function, that will be executed in system mode,
        # but is specific for this systemcall
        syscall = Function("syscall_" + function.function_name,
                           "void", ["int"], extern_c = True)
        self.generator.source_file.function_manager.add(syscall)
        # The syscall function is called from the function that will
        # be inlined into the application
        self.call_function(function, "syscall", "void", [syscall.function_name, str(systemcall.abb.abb_id)])

        if systemcall.function == "TerminateTask":
            self.TerminateTask(syscall, systemcall.abb)
        elif systemcall.function == "ActivateTask":
            self.ActivateTask(syscall, systemcall.abb)
        elif systemcall.function == "ChainTask":
            self.ChainTask(syscall, systemcall.abb)
        else:
            assert False, "Not yet supported %s"% systmcall.function

        self.system_leave_hook(function)

        if systemcall.rettype != 'void':
            self.return_statement(function, "E_OK")



class TaskListTemplate(CodeTemplate):
    def __init__(self, rules):
        CodeTemplate.__init__(self, rules.generator, "os/scheduler/tasklist.h.in")
        self.rules = rules
        self.system_graph = self.generator.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.rules.objects
        self.idle = self.system_graph.find_function("Idle")
        # Link the foreach_subtask method from the rules
        self.foreach_subtask = self.rules.foreach_subtask

        self.__head_signature_vc = self.generator.signature_generator.new()
        # Generate signatures for each task for prio and id
        for subtask in self.system_graph.get_subtasks():
            self.objects[subtask]["task_id_sig"] = self.generator.signature_generator.new()
            self.objects[subtask]["task_prio_sig"] = self.generator.signature_generator.new()

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

    def ready_flag_constructor(self, snippet, args):
        def do(subtask):
            return self.expand_snippet("ready_flag_init", name = subtask.name)

        return self.foreach_subtask(do)

    def task_set_call(self, snippet, args):
        def do(subtask):
            return self.expand_snippet("task_set_entry", 
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



class SchedulerTemplate(CodeTemplate):
    def __init__(self, rules):
        CodeTemplate.__init__(self, rules.generator, "os/scheduler/scheduler.h.in")
        self.rules = rules
        self.system_graph = self.generator.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.rules.objects

        # Link the foreach_subtask method from the rules
        self.foreach_subtask = self.rules.foreach_subtask

    def arbitrary_new_signature(self, snippet, args):
        return str(self.generator.signature_generator.new())

    def current_task_sig(self, snippet, args):
        return str(self.objects["Scheduler"]["current_task_sig"])
    def current_prio_sig(self, snippet, args):
        return str(self.objects["Scheduler"]["current_prio_sig"])

    # Reschedule
    def reschedule_foreach_task(self, snippet, args):
        def do(subtask):
            return self.expand_snippet("reschedule_dispatch_task",
                                       task = self.objects[subtask]["task_descriptor"].name
            )

        return self.foreach_subtask(do)

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


class AlarmTemplate(CodeTemplate):
    def __init__(self, rules):
        CodeTemplate.__init__(self, rules.generator, "os/alarm.h.in")
        self.rules = rules
        self.system_graph = self.generator.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.rules.objects

        # Link the foreach_subtask method from the rules
        self.foreach_subtask = self.rules.foreach_subtask

