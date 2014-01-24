from generator.elements import *
from generator.tools import flatten

import re

""" The debug comments for each replacement rule is only for rules which
classname, that re.match any of these regular expressions"""
trace_rule_patterns = ['.*']

class Generator:

    """Base class of all generators"""
    def __init__(self, system_graph, operations):
        self.system_graph = system_graph
        self.system_description = system_graph.system
        self.rtsc_analysis = system_graph.rtsc
        self.operations = operations
        self.rules = []
        self.__used_variable_names = set()

        operations.set_generator(self)

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


    def generate_into(self, output_file):
        """Generate into output file"""
        self.source_file = SourceFile()

        #include "os.h"
        self.source_file.includes.add(Include("os.h"))

        os_main = Function("os_main", "void", [], extern_c = True)
        os_main.add( FunctionCall("StartOS", ["0"]) )
        self.source_file.function_manager.add(os_main)

        StartOS = Function("StartOS", "void", ["int"])
        self.operations.StartOS(StartOS)
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

            syscall = SystemCall(syscall.type, abb, rettype, function.arguments())
            self.operations.systemcall(syscall, function)

            self.source_file.function_manager.add(function)

        # Write source file to file
        fd = open(output_file, "w")
        contents = self.source_file.expand(self)
        fd.write(contents)
        fd.close()

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

