from generator.rules.simple import SimpleSystem, AlarmTemplate
from generator.elements import CodeTemplate, Include, VariableDefinition, \
    Block, Statement, Comment

class UnencodedSystem(SimpleSystem):
    def __init__(self):
        SimpleSystem.__init__(self)
        self.task_list = TaskListTemplate
        self.scheduler = SchedulerTemplate
        self.alarms = AlarmTemplate

    def id(self, subtask):
        """Returns a string that generates the task id"""
        task_desc = self.objects[subtask]["task_descriptor"].name
        return task_desc

    def sigs(self, count):
        return ""

    def generate_system_code(self):
        self.generator.source_file.includes.add(Include("os/scheduler/tasklist.h"))
        self.generator.source_file.declarations.append(self.task_list(self).expand())

        self.generator.source_file.includes.add(Include("os/scheduler/scheduler.h"))
        self.generator.source_file.includes.add(Include("os/scheduler/task.h"))
        self.generator.source_file.declarations.append(self.scheduler(self).expand())

        self.generator.source_file.includes.add(Include("os/alarm.h"))
        self.generator.source_file.declarations.append(self.alarms(self).expand())

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
                                   "scheduler_.SetReadyFromSuspended_impl",
                                   "void", [self.objects[subtask]["task_descriptor"].name])


            if subtask.autostart and (not highestTask or subtask.static_priority > highestTask.static_priority):
                highestTask = subtask

        self.call_function(block, "Machine::enable_interrupts", "void", [])
        # Call a full reschedule
        self.call_function(block, "syscall", "void", ["os::scheduler::ScheduleC_impl", "0"])
        self.call_function(block, "Machine::unreachable", "void", [])

    def encode_arguments(self, block, arguments):
        encoded_count = len(arguments)
        ## FIXME: We could use a custom struct here
        var = VariableDefinition.new(self.generator, "uint16_t",
                                     array_length = encoded_count)
        encoding_block = Block("/* Arguments */ ")
        block.prepend(encoding_block)
        block.prepend(var)

        for i in range(0, len(arguments)):
            arg = arguments[i][0]
            encoding_block.add(Statement("%s[%d] = %s" % (var.name, i, arg)))
        return var

    def get_encoded_args(self, function, encoded_arguments, arg):
        datatype = encoded_arguments.datatype + "*"
        decl = VariableDefinition.new(self.generator, datatype)
        function.add(decl)
        function.add(Statement("%s = (%s) %s" %(decl.name, datatype, arg[0])))
        return decl

    def get_calling_task_desc(self, abb):
        return self.objects[abb.function.subtask]['task_descriptor']

    def TerminateTask(self, block, abb):
        self.call_function(block, "scheduler_.TerminateTask_impl",
                           "void",
                           [self.objects[abb.function.subtask]['task_descriptor'].name])

    def ActivateTask(self, block, abb):
        self.call_function(block,
                           "scheduler_.ActivateTask_impl" + self.sigs(1),
                           "void",
                           [self.id(abb.arguments[0])])

    def ChainTask(self, block, abb):
        self.call_function(block,
                           "scheduler_.ChainTask_impl" + self.sigs(2),
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
        CodeTemplate.__init__(self, rules.generator, self.template_file())
        self.rules = rules
        self.system_graph = self.generator.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.rules.objects
        self.idle = self.system_graph.find_function("Idle")
        # Link the foreach_subtask method from the rules
        self.foreach_subtask = self.rules.foreach_subtask

    def template_file(self):
        return "os/scheduler/tasklist-unencoded.h.in"

    def ready_flag_variables(self, snippet, args):
        def do(subtask):
            # Intantiate the correct macros
            return self.expand_snippet("ready_flag",
                                       name = subtask.name) + "\n"

        return self.foreach_subtask(do)

    def ready_flag_constructor(self, snippet, args):
        def do(subtask):
            return self.expand_snippet("ready_flag_init", name = subtask.name)

        return self.foreach_subtask(do)

    def task_set_call(self, snippet, args):
        def do(subtask):
            return self.expand_snippet(args[0],
                                       name = subtask.name,
                                       id = self.objects[subtask]["task_id"])

        return self.foreach_subtask(do)

    # Implementation of head
    def head_update_max_cascade(self, snippet, args):
        """Generate the update max cascade for tasklist::head"""
        def do(subtask):
            # Generate a new signature for this cascade step
            do.i += 1
            return self.expand_snippet("head_update_max",
                                       task = subtask.name,
                                       task_id  = self.objects[subtask]["task_id"],
                                       i = str(do.i-1),
                                       ii = str(do.i)
                                       )
        # This is a ugly hack to fix python binding madness
        do.i = 0
        ret = self.foreach_subtask(do)

        # Update current prio for idle task
        ret += self.expand_snippet("head_update_idle_prio",
                                   i = str(do.i), ii = str(do.i + 1))

        return ret



class SchedulerTemplate(CodeTemplate):
    def __init__(self, rules):
        CodeTemplate.__init__(self, rules.generator, self.template_file())
        self.rules = rules
        self.system_graph = self.generator.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.rules.objects

        # Link the foreach_subtask method from the rules
        self.foreach_subtask = self.rules.foreach_subtask

    def template_file(self):
        return "os/scheduler/scheduler-unencoded.h.in"

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
            return self.expand_snippet("activate_task_task",
                                       task = self.objects[subtask]["task_descriptor"].name,
                                       )

        return self.foreach_subtask(do)

