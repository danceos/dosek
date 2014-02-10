from generator.rules.simple import SimpleSystem, AlarmTemplate
from generator.elements import CodeTemplate, Include, Function, VariableDefinition, \
    Block, Statement, Comment

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
        self.objects["Scheduler"]["scheduler_prio_sig"] = self.generator.signature_generator.new()
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
        block.unused_parameter(0)
        highestTask = None
        for subtask in self.system_graph.get_subtasks():
            if not subtask.is_real_thread():
                continue
            # Use Reset the stack pointer for all all tasks
            self.call_function(block,
                               self.objects[subtask]["task_descriptor"].name + ".tcb.reset",
                               "void", [])

            if subtask.autostart:
                self.call_function(block,
                                   "scheduler_.SetReady_impl",
                                   "void", [self.objects[subtask]["task_descriptor"].name])


            if subtask.autostart and (not highestTask or subtask.static_priority > highestTask.static_priority):
                highestTask = subtask

        self.call_function(block, "Machine::enable_interrupts", "void", [])
        # Call a full reschedule
        self.call_function(block, "syscall", "void", ["os::scheduler::ScheduleC_impl", "0"])
        self.call_function(block, "Machine::unreachable", "void", [])

    def encode_arguments(self, block, arguments):
        encoded_count = len(arguments);
        b = self.generator.signature_generator.new()
        ## FIXME: We could use a custom struct here
        var = VariableDefinition.new(self.generator, "Encoded_Static<A0, %d>" % b,
                                     array_length = encoded_count)
        encoding_block = Block("/* Encode Arguments */ ")
        block.prepend(encoding_block)
        block.prepend(var)

        for i in range(0, len(arguments)):
            arg = arguments[i][0]
            encoding_block.add(Statement("%s[%d].encode(%s, 0 /* = D */)" % (var.name, i, arg)))
        return var

    def get_encoded_args(self, function, encoded_arguments, arg):
        datatype = encoded_arguments.datatype + "*";
        decl = VariableDefinition.new(self.generator, datatype)
        function.add(decl)
        function.add(Statement("%s = (%s) %s" %(decl.name, datatype, arg[0])))
        return decl

    def get_calling_task_desc(self, abb):
        return self.objects[abb.function.subtask]['task_descriptor']

    def TerminateTask(self, block, abb):
        self.call_function(block, "scheduler_.TerminateTask_impl", "void",
                           [self.objects[abb.function.subtask]['task_descriptor'].name])

    def ActivateTask(self, block, abb):
        self.call_function(block,
                           "scheduler_.ActivateTask_impl",
                           "void",
                           [self.enc_id(abb.arguments[0])])

    def ChainTask(self, block, abb):
        self.call_function(block,
                           "scheduler_.ChainTask_impl",
                           "void",
                           [self.get_calling_task_desc(abb).name,
                            self.objects[abb.arguments[0]]['task_descriptor'].name])

    def SetRelAlarm(self, kernelspace, abb, encoded_args):
        # We have to encode 2 arguments, there
        args = self.get_encoded_args(kernelspace, encoded_args, kernelspace.arguments()[0])
        alarm_id = abb.arguments[0]
        alarm_object = self.objects["alarm"][alarm_id]
        self.call_function(kernelspace, "%s.setRelativeTime" % alarm_object.name,
                           "void", ["%s[0]" % args.name])
        self.call_function(kernelspace, "%s.setCycleTime" % alarm_object.name,
                           "void", ["%s[1]" % args.name])
        self.call_function(kernelspace, "%s.setArmed" % alarm_object.name,
                           "void", ["true"])
        kernelspace.add(Comment("Dispatch directly back to Userland"))
        self.call_function(kernelspace, "Dispatcher::ResumeToTask",
                           "void",
                           [self.get_calling_task_desc(abb).name])

    def CancelAlarm(self, kernelspace, abb):
        alarm_id = abb.arguments[0]
        alarm_object = self.objects["alarm"][alarm_id]
        self.call_function(kernelspace, "%s.setArmed" % alarm_object.name,
                           "void", ["false"])
        kernelspace.add(Comment("Dispatch directly back to Userland"))
        self.call_function(kernelspace, "Dispatcher::ResumeToTask",
                           "void",
                           [self.get_calling_task_desc(abb).name])

    def GetResource(self, kernelspace, abb):
        next_prio = abb.definite_after('local').dynamic_priority
        self.call_function(kernelspace,
                           "scheduler_.GetResource_impl",
                           "void",
                           [self.get_calling_task_desc(abb).name,
                            str(next_prio)])

        kernelspace.add(Comment("Dispatch directly back to Userland"))
        self.call_function(kernelspace, "Dispatcher::ResumeToTask",
                           "void",
                           [self.get_calling_task_desc(abb).name])

    def ReleaseResource(self, kernelspace, abb):
        next_prio = abb.definite_after('local').dynamic_priority
        self.call_function(kernelspace,
                           "scheduler_.ReleaseResource_impl",
                           "void",
                           [self.get_calling_task_desc(abb).name,
                            str(next_prio)])

    def systemcall(self, systemcall, userspace):
        """Generate systemcall into userspace"""
        self.system_enter_hook(userspace)

        subtask = systemcall.abb.function.subtask
        abb_id  = systemcall.abb.abb_id
        func_syscall_block = self.generator.arch_rules.syscall_block


        if systemcall.function == "TerminateTask":
            syscall = func_syscall_block(userspace, subtask, abb_id)
            self.TerminateTask(syscall, systemcall.abb)
        elif systemcall.function == "ActivateTask":
            userspace.unused_parameter(0)
            syscall = func_syscall_block(userspace, subtask, abb_id)
            self.ActivateTask(syscall, systemcall.abb)
        elif systemcall.function == "ChainTask":
            userspace.unused_parameter(0)
            syscall = func_syscall_block(userspace, subtask, abb_id)
            self.ChainTask(syscall, systemcall.abb)
        elif systemcall.function == "CancelAlarm":
            userspace.unused_parameter(0)
            syscall = func_syscall_block(userspace, subtask, abb_id)
            self.CancelAlarm(syscall, systemcall.abb)
        elif systemcall.function == "GetResource":
            userspace.unused_parameter(0)
            syscall = func_syscall_block(userspace, subtask, abb_id)
            self.GetResource(syscall, systemcall.abb)
        elif systemcall.function == "ReleaseResource":
            userspace.unused_parameter(0)
            syscall = func_syscall_block(userspace, subtask, abb_id)
            self.ReleaseResource(syscall, systemcall.abb)
        elif systemcall.function == "SetRelAlarm":
            userspace.unused_parameter(0)
            # The SetRelAlarm systemcall needs two arguments from the
            # userspace, so we encode them
            encoded_args = self.encode_arguments(userspace, userspace.arguments()[1:])
            # A Pointer to the encoded args is given
            syscall = func_syscall_block(userspace, subtask, "&" + encoded_args.name)
            self.SetRelAlarm(syscall, systemcall.abb, encoded_args)
        else:
            assert False, "Not yet supported %s"% systemcall.function

        self.system_leave_hook(userspace)

        if systemcall.rettype != 'void':
            self.return_statement(userspace, "E_OK")



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
    def scheduler_prio_sig(self, snippet, args):
        return str(self.objects["Scheduler"]["scheduler_prio_sig"])

    def scheduler_prio(self, snippet, args):
        max_prio = 0
        for subtask in self.system_graph.get_subtasks():
            if not subtask.is_real_thread():
                continue
            if(subtask.static_priority > max_prio):
                max_prio = subtask.static_priority

        return str(max_prio+1)

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

