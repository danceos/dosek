from generator.primitives import *
from generator.atoms import *
from generator.tools import flatten

import re

""" The debug comments for each replacement rule is only for rules which
classname, that re.match any of these regular expressions"""
trace_rule_patterns = ['.*']

class Generator:

    """Base class of all generators"""
    def __init__(self, system_description, object_file, analysis):
        self.system_description = system_description
        self.object_file = object_file
        self.analysis = analysis
        self.rules = []
        self.__used_variable_names = set()

    OSEK_CALLS = {
        "OSEKOS_ActivateTask": ["StatusType", "TaskType"],
        "OSEKOS_ChainTask": ["StatusType", "TaskType"],
        "OSEKOS_TerminateTask": ["StatusType"],
        "OSEKOS_Schedule": ["StatusType"],
        "OSEKOS_GetTaskID": ["StatusType", "TaskRefType"],
        "OSEKOS_GetTaskState": ["StatusType", "TaskType", "TaskStateRefType"],

        "OSEKOS_EnableAllInterrupts": ["void"],
        "OSEKOS_DisableAllInterrupts": ["void"],
        "OSEKOS_ResumeAllInterrupts": ["void"],
        "OSEKOS_SuspendAllInterrupts": ["void"],
        "OSEKOS_ResumeOSInterrupts": ["void"],
        "OSEKOS_SuspendOSInterrupts": ["void"],

        "OSEKOS_GetResource": ["StatusType", "ResourceType"],
        "OSEKOS_ReleaseResource": ["StatusType", "ResourceType"],

        "OSEKOS_SetEvent": ["StatusType", "TaskType", "EventMaskType"],
        "OSEKOS_GetEvent": ["StatusType", "TaskType", "EventMaskRefType"],
        "OSEKOS_ClearEvent": ["StatusType", "EventMaskType"],
        "OSEKOS_WaitEvent": None,
        "OSEKOS_GetAlarm": None,
        "OSEKOS_SetRelAlarm": None,
        "OSEKOS_SetRelAlarm": None,
        "OSEKOS_CancelAlarm": None,
        "OSEKOS_GetAlarmBase": None,
        "OSEKOS_AdvanceCounter": None,
        "OSEKOS_SendMessage": None,
        "OSEKOS_ReceiveMessage": None,
        "OSEKOS_SendDynamicMessage": None,
        "OSEKOS_ReceiveDynamicMessage": None,
        "OSEKOS_SendZeroMessage": None,
        "OSEKOS_ShutdownOS": ["void", "StatusType"]    }

    def generate_into(self, output_file):
        """Generate into output file"""
        self.source_file = SourceFile()

        #include "os.h"
        self.source_file.includes.add(Include("os.h"))

        # find all
        for symbol in self.object_file.get_undefined_symbols():
            for system_call in self.OSEK_CALLS:
                if symbol.startswith(system_call):
                    tmp = symbol.split("__ABB")
                    assert len(tmp) == 2

                    rettype = self.OSEK_CALLS[system_call][0]
                    argtypes = self.OSEK_CALLS[system_call][1:]
                    syscall = tmp[0]
                    abb = int(tmp[1])

                    # Generate all atoms into a function block
                    function = Function(symbol,
                                        rettype,
                                        argtypes,
                                        extern_c = True)

                    return_variable = VariableDefinition.atom(self, rettype)
                    if return_variable != None:
                        seed_atoms = [Hook.atom("SystemEnterHook"),
                                      return_variable,
                                      SystemCall.atom(syscall, abb,  return_variable["name"],
                                                      function.arguments()),
                                      Hook.atom("SystemLeaveHook"),
                                      Statement.atom_return(return_variable["name"])]
                    else:
                        seed_atoms = [Hook.atom("SystemEnterHook"),
                                      SystemCall.atom(syscall, abb,  None,
                                                      function.arguments()),
                                      Hook.atom("SystemLeaveHook")]

                    atoms = self.run_rules(seed_atoms)
                    # instanciate all atoms
                    for atom in atoms:
                        self.instantiate_atom(function, atom)

                    # Add function to the generated source file
                    self.source_file.function_manager.add(function)

        # Write source file to file
        fd = open(output_file, "w+")
        contents = self.source_file.expand(self)
        fd.write(contents)
        fd.close()

    def instantiate_atom(self, block, atom):
        cls = atom['__token']
        # Instanciate all objects
        for obj in atom.get("__references_objects", []):
            self.source_file.data_manager.add(obj)
        # Include all used headers
        for header in atom.get("__references_headers", []):
            self.source_file.includes.add(Include(header))

        args = dict([(k, v) for (k,v) in atom.items()
                     if not k.startswith("__")])
        obj = cls(**args)
        if Block.isa(atom):
            for x in atom["__statements"]:
                self.instantiate_atom(obj, x)
        block.add(obj)

    def load_rules(self, rules):
        self.rules += rules
        # Sort rules by priority
        self.rules = list(sorted(self.rules, key= lambda x: x.prio))


    @staticmethod
    def is_rule_traced(rule):
        global trace_rule_patterns
        for pattern in trace_rule_patterns:
            if re.match(pattern, rule.__class__.__name__):
                return True
        return False

    def run_rules(self, seed_atoms):
        seq = seed_atoms

        def replace_till_change(sequence):
            for rule in self.rules:
                for idx in range(0, len(sequence)):
                    if Block.isa(sequence[idx]):
                        repl, changed = replace_till_change(sequence[idx]["__statements"])
                        if changed:
                            sequence[idx]["__statements"] = repl
                            return sequence, True
                    elif rule.matches(self, sequence, idx):
                        sequence = rule.replace(self, sequence, idx)
                        # We changed something. Restart replacement process
                        return sequence, True
            return sequence, False
        while True:
            seq, changed = replace_till_change(seq)

            # Nothing Changed? Stop replacement function
            if changed == False:
                break
        return seq

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

