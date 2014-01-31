from generator.elements import *
import logging

class SignatureGenerator:
    def __init__(self, start = 1000):
        self.sig = start
        self.used = set()
    def new(self):
        i = 1
        while (self.sig + i) in self.used:
            i += 1
        x = self.sig + i
        self.sig = x
        self.used.add(x)
        return x
    def lessthan(self, other):
        i = 1
        while (other - i) in self.used:
            i += 1
        x = other - i
        assert x > 0
        self.used.add(x)
        return x


class Generator:

    """Base class of all generators"""
    def __init__(self, system_graph, name, os_rules, arch_rules):
        self.name = name
        self.system_graph = system_graph
        self.system_description = system_graph.system
        self.rtsc_analysis = system_graph.rtsc
        self.os_rules = os_rules
        self.arch_rules = arch_rules
        self.rules = []
        self.__used_variable_names = set()
        self.template_base = None
        self.signature_generator = SignatureGenerator()

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


    OSEK_CALLS = {
        "ActivateTask": ["StatusType", "TaskType"],
        "ChainTask": ["StatusType", "TaskType"],
        "TerminateTask": ["StatusType"],
        "Schedule": ["StatusType"],
        "GetTaskID": ["StatusType", "TaskRefType"],
        "GetTaskState": ["StatusType", "TaskType", "TaskStateRefType"],

        "EnableAllInterrupts": ["void"],
        "DisableAllInterrupts": ["void"],
        "ResumeAllInterrupts": ["void"],
        "SuspendAllInterrupts": ["void"],
        "ResumeOSInterrupts": ["void"],
        "SuspendOSInterrupts": ["void"],

        "GetResource": ["StatusType", "ResourceType"],
        "ReleaseResource": ["StatusType", "ResourceType"],

        "SetEvent": ["StatusType", "TaskType", "EventMaskType"],
        "GetEvent": ["StatusType", "TaskType", "EventMaskRefType"],
        "ClearEvent": ["StatusType", "EventMaskType"],
        "WaitEvent": None,
        "GetAlarm": None,
        "SetRelAlarm": None,
        "CancelAlarm": None,
        "GetAlarmBase": None,
        "AdvanceCounter": None,
        "SendMessage": None,
        "ReceiveMessage": None,
        "SendDynamicMessage": None,
        "ReceiveDynamicMessage": None,
        "SendZeroMessage": None,
        "ShutdownOS": ["void", "StatusType"]    }


    def generate_into(self, output_file_prefix):
        """Generate into output file"""
        self.file_prefix = output_file_prefix
        self.source_file = SourceFile()
        self.source_files["coredos.cc"] = self.source_file

        #include "os.h"
        self.source_file.includes.add(Include("os.h"))

        # Generate system objects
        self.os_rules.generate_dataobjects()

        # Generate all nessecary code elements for the system (except
        # the concrete calls from the application
        self.os_rules.generate_system_code()

        # Only generate an os_main, if it does not exist
        if not "os_main" in self.system_graph.functions:
            logging.info("Generating an os_main function calling StartOS")
            os_main = Function("os_main", "void", [], extern_c = True)
            os_main.add( FunctionCall("StartOS", ["0"]) )
            self.source_file.function_manager.add(os_main)

        StartOS = Function("StartOS", "void", ["int"], extern_c = True)
        self.os_rules.StartOS(StartOS)
        self.source_file.function_manager.add(StartOS)

        # find all
        for syscall in self.system_graph.get_syscalls():
            if syscall.type in ("Idle", "StartOS"):
                continue
            generated_function = "OSEKOS_%s__ABB%d" %(syscall.type, syscall.abb_id)
            rettype  = self.OSEK_CALLS[syscall.type][0]
            argtypes = self.OSEK_CALLS[syscall.type][1:]
            abb      = syscall

            # Generate all atoms into a function block
            function = Function(generated_function,
                                rettype,
                                argtypes,
                                extern_c = True)

            assert abb.function.subtask != None, "The calling subtask must be set"
            self.objects[abb.function.subtask]["generated_functions"].append(function)

            syscall = SystemCall(syscall.type, abb, rettype, function.arguments())
            self.os_rules.systemcall(syscall, function)

            self.source_file.function_manager.add(function)

        # Write source files to file
        for name in self.source_files:
            with self.open_file(name) as fd:
                contents = self.source_files[name].expand(self)
                fd.write(contents)

        self.arch_rules.generate_linkerscript()

    def open_file(self, name, mode = "w+"):
        fd = open(self.file_prefix + "/" + self.name + "_" + name, "w+")
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
        datatype = datatype.replace("::", "_")
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

