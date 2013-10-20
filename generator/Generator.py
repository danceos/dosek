from generator.primitives import *
from generator.atoms import *
from generator.types import *

class Generator:

    """Base class of all generators"""
    def __init__(self, system_description, object_file):
        self.system_description = system_description
        self.object_file = object_file
        self.rules = []

    OSEK_CALLS = {
        "OSEKOS_ActivateTask": [StatusType, TaskType],
        "OSEKOS_ChainTask": [StatusType, TaskType],
        "OSEKOS_TerminateTask": [StatusType],
        "OSEKOS_Schedule": [StatusType],
        "OSEKOS_GetTaskID": [StatusType, TaskRefType],
        "OSEKOS_GetTaskState": [StatusType, TaskType, TaskStateRefType],

        "OSEKOS_EnableAllInterrupts": [void],
        "OSEKOS_DisableAllInterrupts": [void],
        "OSEKOS_ResumeAllInterrupts": [void],
        "OSEKOS_SuspendAllInterrupts": [void],
        "OSEKOS_ResumeOSInterrupts": [void],
        "OSEKOS_SuspendOSInterrupts": [void],

        "OSEKOS_GetResource": [StatusType, ResourceType],
        "OSEKOS_ReleaseResource": [StatusType, ResourceType],

        "OSEKOS_SetEvent": [StatusType, TaskType, EventMaskType],
        "OSEKOS_GetEvent": [StatusType, TaskType, EventMaskRefType],
        "OSEKOS_ClearEvent": [StatusType, EventMaskType],
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
        "OSEKOS_ShutdownOS": [void, StatusType]    }

    def generate_into(self, output_file):
        """Generate into output file"""
        self.source_file = SourceFile()

        # find all
        for symbol in self.object_file.get_undefined_symbols():
            for system_call in self.OSEK_CALLS:
                if symbol.startswith(system_call):
                    tmp = symbol.split("__")
                    assert len(tmp) == 2

                    rettype = self.OSEK_CALLS[system_call][0]
                    argtypes = self.OSEK_CALLS[system_call][1:]
                    syscall = tmp[0]
                    abb = int(tmp[1])

                    # Generate all atoms into a function block
                    function = Function(symbol,
                                        rettype,
                                        argtypes)

                    seed_atom = {'token': SystemCall,
                                 'syscall': syscall,
                                 'abb': abb,
                                 'rettype': rettype,
                                 'arguments': function.arguments()}

                    atoms = self.run_rules(seed_atom)
                    # instanciate all atoms
                    atoms = [self.instanciate_atom(x) for x in atoms]


                    for atom in atoms:
                        if hasattr(atom, 'generate_into'):
                            atom.generate_into(self, function)
                        else:
                            function.add(atom)

                    # Add function to the generated source file
                    self.source_file.function_manager.add(function)

        # Write source file to file
        fd = open(output_file, "w+")
        fd.write(self.source_file.generate())
        fd.close()

    def instanciate_atom(self, atom):
        cls = atom['token']
        args = dict([(k, v) for (k,v) in atom.items()
                    if k != "token"])
        return cls(**args)


    def load_rules(self, rules):
        self.rules += rules
        # Sort rules by priority
        self.rules = list(sorted(self.rules, key= lambda x: x.prio))

    def run_rules(self, seed_atom):
        seq = [seed_atom]

        while True:
            changed = False

            for rule in self.rules:
                for idx in range(0, len(seq)):
                    if rule.matches(seq, idx):
                        seq = rule.replace(seq, idx)
                        # We changed something. Restart replacement process
                        changed = True
                        break
                if changed == True:
                    break

            # Nothing Changed? Stop replacement function
            if changed == False:
                break

        return seq

