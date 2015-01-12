from generator.elements import *
from generator.rules import SignatureGenerator
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
        number_of_tasks = len([x for x in self.system_graph.get_subtasks()
                               if not x.is_isr])
        self.signature_generator = SignatureGenerator(number_of_tasks)

        self.file_prefix = None
        self.source_file = None
        self.source_files = dict()

        self.objects = dict()
        # Intialize dicts for all subtasks in the objects tree
        for subtask in self.system_graph.get_subtasks():
            if not subtask in self.objects:
                self.objects[subtask] = {}
                self.objects[subtask]["generated_functions"] = []

        os_rules.set_generator(self)
        arch_rules.set_generator(self)
        syscall_rules.set_generator(self)

    OSEK_CALLS = {
        "kickoff" : ["void"],
        "ActivateTask": ["StatusType", "TaskType"],
        "ChainTask": ["StatusType", "TaskType"],
        "TerminateTask": ["StatusType"],
        "Schedule": None, # ["StatusType"],
        "GetTaskID": None, # ["StatusType", "TaskRefType"],
        "GetTaskState": None, # ["StatusType", "TaskType", "TaskStateRefType"],

        "EnableAllInterrupts"  : ["void"],
        "DisableAllInterrupts" : ["void"],
        "ResumeAllInterrupts"  : ["void"],
        "SuspendAllInterrupts" : ["void"],
        "ResumeOSInterrupts"   : ["void"],
        "SuspendOSInterrupts"  : ["void"],

        "GetResource": ["StatusType", "ResourceType"],
        "ReleaseResource": ["StatusType", "ResourceType"],

        "SetEvent": None, # ["StatusType", "TaskType", "EventMaskType"],
        "GetEvent": None, # ["StatusType", "TaskType", "EventMaskRefType"],
        "ClearEvent": None, #["StatusType", "EventMaskType"],
        "WaitEvent": None,
        "GetAlarm": ["StatusType", "AlarmType", "TickRefType"],
        "SetRelAlarm": ["StatusType", "AlarmType", "TickType", "TickType"],
        "CancelAlarm": ["StatusType", "AlarmType"],
        "GetAlarmBase": None,
        "AdvanceCounter": ["StatusType", "AlarmType"],
        "SendMessage": None,
        "ReceiveMessage": None,
        "SendDynamicMessage": None,
        "ReceiveDynamicMessage": None,
        "SendZeroMessage": None,
        "ShutdownOS": ["void", "StatusType"],

        "AcquireCheckedObject": ["void", "dep::Checked_Object*"],
        "ReleaseCheckedObject": ["void", "dep::Checked_Object*"] }


    def generate_into(self, output_file_prefix):
        """Generate into output file"""
        self.file_prefix = output_file_prefix
        self.source_file = SourceFile()
        self.source_files["dosek.cc"] = self.source_file
        

        #include "os.h"
        self.source_file.includes.add(Include("os.h"))

        # Generate system objects
        self.arch_rules.generate_dataobjects()
        self.os_rules.generate_dataobjects()

        # Generate all necessary code elements for the system (except
        # the concrete calls from the application
        self.os_rules.generate_system_code()

        # Only generate an os_main, if it does not exist
        if not "os_main" in self.system_graph.functions:
            logging.info("Generating an os_main function calling StartOS")
            os_main = Function("os_main", "void", [], extern_c = True)
            os_main.add( FunctionCall("StartOS", ["0"]) )
            self.source_file.function_manager.add(os_main)

        # Generate a StartOS function and delegate it to the OS rule set
        StartOS = Function("StartOS", "void", ["int"], extern_c = True)
        self.objects["StartOS"] = StartOS
        self.syscall_rules.StartOS(StartOS)
        self.source_file.function_manager.add(StartOS)

        # Generate the interrupt scheduler
        ASTSchedule = Function("__OS_ASTSchedule", "void", ["int"], extern_c = True)
        self.objects["ASTSchedule"] = ASTSchedule
        self.syscall_rules.ASTSchedule(ASTSchedule)
        self.source_file.function_manager.add(ASTSchedule)

        # find all syscalls
        for syscall in self.system_graph.get_syscalls():
            if not syscall.syscall_type.isRealSyscall():
                continue
            generated_function = syscall.generated_function_name()
            rettype  = self.OSEK_CALLS[syscall.syscall_type.name][0]
            argtypes = self.OSEK_CALLS[syscall.syscall_type.name][1:]
            abb      = syscall

            # Add function definition for the function that is
            # _called_ by the application (with __ABB suffix)
            function = Function(generated_function,
                                rettype,
                                argtypes,
                                extern_c = True)
            self.stats.add_data(syscall, "generated-function", function.name)

            assert abb.function.subtask != None, "The calling subtask must be set"
            self.objects[abb.function.subtask]["generated_functions"].append(function)

            syscall = SystemCall(syscall.syscall_type.name, abb, rettype, function.arguments())
            self.os_rules.systemcall(syscall, function)

            self.source_file.function_manager.add(function)

        # Generate the hooks into the operating system
        self.os_rules.generate_hooks()

        # Generate systemcalls
        isrs = []
        for isr in self.system_graph.get_subtasks():
            if isr.is_isr and isr.isr_device:
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

