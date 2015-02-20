from generator.elements import *
from generator.graph.Function import Function as GraphFunction
from generator.graph.types import S
from .rules.implementations import *
from .rules import SignatureGenerator

import logging

class Generator:
    """Base class of all generators"""
    def __init__(self, system_graph, name, arch_rules, os_rules, syscall_rules):
        self.name = name
        self.system_graph = system_graph
        self.stats = system_graph.stats
        self.arch_rules = arch_rules
        self.os_rules = os_rules
        self.syscall_rules = syscall_rules
        self.rules = []
        self.__used_variable_names = set()
        self.template_base = None
        number_of_tasks = len(self.system_graph.user_subtasks)

        self.signature_generator = SignatureGenerator(number_of_tasks)

        self.file_prefix = None
        self.source_file = None
        self.source_files = dict()

        os_rules.set_generator(self)
        arch_rules.set_generator(self)
        syscall_rules.set_generator(self)

    OSEK_CALLS = {
        S.kickoff : ["void"],
        S.ActivateTask: ["StatusType", "TaskType"],
        S.ChainTask: ["StatusType", "TaskType"],
        S.TerminateTask: ["StatusType"],
        #S.Schedule: None, # ["StatusType"],
        #S.GetTaskID: None, # ["StatusType", "TaskRefType"],
        #S.GetTaskState: None, # ["StatusType", "TaskType", "TaskStateRefType"],
        
        S.EnableAllInterrupts  : ["void"],
        S.DisableAllInterrupts : ["void"],
        S.ResumeAllInterrupts  : ["void"],
        S.SuspendAllInterrupts : ["void"],
        S.ResumeOSInterrupts   : ["void"],
        S.SuspendOSInterrupts  : ["void"],

        S.GetResource: ["StatusType", "ResourceType"],
        S.ReleaseResource: ["StatusType", "ResourceType"],

        S.SetEvent: ["StatusType", "TaskType", "EventMaskType"],
        # S.GetEvent: None, # ["StatusType", "TaskType", "EventMaskRefType"],
        S.ClearEvent: ["StatusType", "EventMaskType"],
        S.WaitEvent: ["StatusType", "EventMaskType"],

        S.GetAlarm: ["StatusType", "AlarmType", "TickRefType"],
        S.SetRelAlarm: ["StatusType", "AlarmType", "TickType", "TickType"],
        S.CancelAlarm: ["StatusType", "AlarmType"],
        #S.GetAlarmBase: None,
        S.AdvanceCounter: ["StatusType", "AlarmType"],
        #S.SendMessage: None,
        #S.ReceiveMessage: None,
        #S.SendDynamicMessage: None,
        #S.ReceiveDynamicMessage: None,
        #S.SendZeroMessage: None,
        #S.ShutdownOS: ["void", "StatusType"],

        S.AcquireCheckedObject: ["void", "dep::Checked_Object*"],
        S.ReleaseCheckedObject: ["void", "dep::Checked_Object*"] }


    def generate_into(self, output_file_prefix):
        """Generate into output file"""
        self.file_prefix = output_file_prefix
        self.source_file = SourceFile()
        self.source_files["dosek.cc"] = self.source_file

        #include "os.h"
        self.source_file.includes.add(Include("os.h"))

        self.system_graph.impl = SystemImpl()
        for subtask in self.system_graph.subtasks:
            subtask.impl = SubtaskImpl()

        # Generate system objects
        self.arch_rules.generate_dataobjects()
        self.os_rules.generate_dataobjects()

        # Generate all necessary code elements for the system (except
        # the concrete calls from the application
        self.os_rules.generate_system_code()

        # Only generate an os_main, if it does not exist
        if self.system_graph.find(GraphFunction, "os_main") is None:
            logging.info("Generating an os_main function calling StartOS")
            os_main = Function("os_main", "void", [], extern_c = True)
            os_main.add( FunctionCall("StartOS", ["0"]) )
            self.source_file.function_manager.add(os_main)

        # Generate a StartOS function and delegate it to the OS rule set
        StartOS = Function("StartOS", "void", ["int"], extern_c = True)
        self.syscall_rules.StartOS(StartOS)
        self.source_file.function_manager.add(StartOS)
        self.system_graph.impl.StartOS = StartOS

        # Generate the interrupt scheduler
        ASTSchedule = Function("__OS_ASTSchedule", "void", ["int"], extern_c = True)
        self.syscall_rules.ASTSchedule(ASTSchedule)
        self.source_file.function_manager.add(ASTSchedule)

        # find all syscalls
        for abb in self.system_graph.real_syscalls:
            assert abb.subtask != None, "The calling subtask must be set"

            generated_function = abb.generated_function_name()
            abb.impl = SyscallImplementation()
            abb.impl.rettype  = self.OSEK_CALLS[abb.syscall_type][0]
            abb.impl.argtypes = self.OSEK_CALLS[abb.syscall_type][1:]

            # Add function definition for the function that is
            # _called_ by the application (with __ABB suffix)
            userspace = Function(generated_function, abb.impl.rettype, abb.impl.argtypes,
                                 extern_c = True)
            self.stats.add_data(abb, "generated-function", userspace.name)
            abb.impl.userspace = userspace

            # Add userspace function to the userspace
            self.source_file.function_manager.add(userspace)

            # Register userspace function at the subtask, since it
            # only callable from there
            abb.subtask.impl.generated_functions.append(userspace)

            self.os_rules.systemcall(abb)

        # Generate the hooks into the operating system
        self.os_rules.generate_hooks()

        # Generate systemcalls
        isrs = []
        for isr in self.system_graph.subtasks:
            if isr.conf.is_isr and isr.conf.isr_device:
                isrs.append(isr)
        self.arch_rules.generate_isr_table(isrs)


        # Write source files to file
        for name in self.source_files:
            with self.open_file(name) as fd:
                contents = self.source_files[name].expand(self)
                fd.write(contents)


        self.arch_rules.generate_linkerscript()

    def open_file(self, name, mode = "w+"):
        fd = open(self.file_prefix + "/" + name, "w+")
        return fd

    def variable_name_for_singleton(self, datatype, instance = None):
        """Returns a unique datatype for singleton creation. This is used for
        global object naming"""
        varname = "var_" + datatype
        if instance != None:
            varname += "_" + instance
        self.__used_variable_names.add(varname)
        return varname

    def variable_name_for_datatype(self, datatype):

        """Generates a new unique variable name for a concrete datatype"""
        for i in range(0, len(datatype)):
            if not datatype[i].isalnum():
                datatype = datatype[:i] + "_" + datatype[i+1:]
        varname = "var_" + datatype
        if not varname in self.__used_variable_names:
            self.__used_variable_names.add(varname)
            return varname
        i = 0
        while ("%s_%d" % (varname, i)) in self.__used_variable_names:
            i += 1
        varname = ("%s_%d" % (varname, i))
        self.__used_variable_names.add(varname)
        return varname

