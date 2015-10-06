from .arch_generic import GenericArch
from .elements import *
from generator.analysis.Subtask import Subtask
import json


class OSEKVArch(GenericArch):
    def __init__(self):
        super(OSEKVArch, self).__init__()

    # config-constraint-: (arch.self == osek-v) -> !arch.mpu
    def generate_linkerscript(self):
        """OSEK-V has a generic linker script"""
        with self.generator.open_file("linker.ld") as fd:
            fd.write("IGNORED IN OSEK-V")

    def generate_dataobjects(self):
        """Generate all dataobjects for the system"""
        self.logic = self.system_graph.get_pass("LogicMinimizer")
        self.generate_dataobjects_task_stacks() # From SimpleArch
        for subtask in self.system_graph.real_subtasks:
            subtask.impl.stack.allocation_prefix +=" __attribute__((aligned(16))) "
        self.generate_dataobjects_task_entries()
        self.generate_dataobjects_task_descriptors()
        self.generate_rocket_config()

        # For dummy ResumeToTask
        self.generator.source_file.include("dispatch.h")

    def generate_dataobjects_task_descriptors(self):
        self.generator.source_file.include("os/scheduler/task.h")
        self.generator.source_file.include("tcb.h")
        self.system_graph.idle_subtask.impl.task_id = 0
        tcb = DataObject("const arch::TCB", "null_tcb")
        tcb.allocation_prefix = "constexpr "
        self.generator.source_file.data_manager.add(tcb, namespace = ("arch",))
        inverse_action_mapping = {v: int(k, 2) for (k, v) in self.logic.fsm.action_mapping.items()}

        for subtask in self.system_graph.real_subtasks:
            # Ignore the Idle thread
            if not subtask.is_real_thread():
                continue
            if not subtask in inverse_action_mapping:
                inverse_action_mapping[subtask] = len(inverse_action_mapping)
                subtask.impl.present = False
            else:
                subtask.impl.present = True
            task_id = inverse_action_mapping[subtask]
            initializer = "(%d, %d, %s, arch::null_tcb)" % (
                task_id,
                subtask.conf.static_priority,
                str(subtask.conf.preemptable).lower(),
            )

            desc = DataObject("const os::scheduler::Task", "OS_" + subtask.name + "_task",
                              initializer)
            desc.allocation_prefix = "constexpr "

            self.generator.source_file.data_manager.add(desc, namespace = ("os", "tasks"))
            subtask.impl.task_descriptor = desc
            subtask.impl.task_id = task_id

    def generate_rocket_config(self):
        static_alarm_pass = self.system_graph.get_pass("static-alarms")
        alarms = {}
        # Generate rocket configuration for static alarms
        if len(static_alarm_pass.static_alarms) > 0:
            static_alarms = []
            entry_abb = self.system_graph.AlarmHandlerSubtask.entry_abb
            exit_abb = self.system_graph.AlarmHandlerSubtask.exit_abb

            for alarm in self.system_graph.AlarmHandlerSubtask.alarms:
                if not alarm in static_alarm_pass.static_alarms:
                    continue
                config = static_alarm_pass.static_alarms[alarm]
                # namedtuple -> OrderedDict -> dict
                config = dict(config._asdict())
                config["name"] = alarm.name
                config["fsm_signal"] = self.syscall_rules.fsm_event_number(alarm.carried_syscall)
                static_alarms.append(config)
            alarm_entry_signal = self.syscall_rules.fsm_event_number(entry_abb)
            alarm_exit_signal = self.syscall_rules.fsm_event_number(exit_abb)
            alarms = {"basePeriod":      static_alarm_pass.base_period,
                      "staticAlarms":    static_alarms,
                      "entrySignal":     alarm_entry_signal,
                      "exitSignal":      alarm_exit_signal,
                      "count":           len(static_alarms)}

        with self.generator.open_file("rocket.config") as fd:
            config = {
                "coreHartCount":   1 << self.logic.action_len,
                "coreOSEKSyscallWidth": self.logic.event_len,
                "coreOSEKStateWidth":   self.logic.state_len,
                "coreOSEKInitialState": int(self.logic.fsm.initial_state, 2),
                "coreHartCombinatorics":self.logic.minimized_truth_table_path,
                "alarms": alarms,
            }
            fd.write(json.dumps(config,indent=2, sort_keys=True))

    def generate_isr_table(self, isrs):
        self.generator.source_file.include("interrupt.h")

        isr_table = DataObjectArray("arch::interrupt_handler_t",
                                    "isr_table", "")
        isr_table.static_initializer = []
        self.generator.source_file.data_manager.add(isr_table, namespace=("arch",))
        for isr in isrs:
            (device, function) = self.generate_isr(isr)
            while (device+1) > len(isr_table.static_initializer):
                isr_table.static_initializer.append("&arch::bad_soft_irq")
            isr_table.static_initializer[device] = "&" + function

    def generate_isr(self, isr):
        isr_desc = self.generator.system_graph.get(Subtask, isr.name)

        handler = Function(isr_desc.function_name + "_wrapper", "void", ["unsigned char"])
        self.generator.source_file.function_manager.add(handler)

        # Call kickoff, user defined function, and iret system call
        kickoff, iret = isr.entry_abb, isr.exit_abb
        handler.unused_parameter(0);
        self.call_function(handler, kickoff.generated_function_name(), "void", [])
        self.call_function(handler, isr.function_name, "void", [])
        self.call_function(handler, iret.generated_function_name(), "void", [])

        forward = FunctionDeclaration(isr.function_name, "void", [], extern_c=True)
        self.generator.source_file.function_manager.add(forward)

        return(isr_desc.conf.isr_device, handler.function_name)

    def generate_kernelspace(self, userspace, abb, arguments):
        """When a systemcall is done from a app (synchroanous syscall), then we
           disable interrupts. In the interrupt handler they are already
           disabled.
        """
        if abb.subtask.conf.is_isr:
            userspace.add(Comment("Called from ISR, no disable interrupts required!"))
        else:
            self.call_function(userspace, "Machine::disable_interrupts", "void", [])

        args = [(arg.name, arg.datatype) for arg in arguments]
        pre_hook  = Hook("SystemEnterHook",arguments =  args)
        system    = Block(arguments = args)
        post_hook = Hook("SystemLeaveHook", userspace.arguments())

        userspace.add(pre_hook)
        userspace.add(system)
        userspace.add(post_hook)

        if abb.subtask.conf.is_isr:
            userspace.add(Comment("Called from ISR, no enable interrupts required!"))
        elif abb.syscall_type.doesTerminateTask():
            userspace.add(Comment("Return with closed interrupts"))
        else:
            self.call_function(userspace, "Machine::enable_interrupts", "void", [])

        return self.KernelSpace(pre_hook, system, post_hook)

    def get_syscall_argument(self, block, i):
        name, typename = block.arguments()[i]
        return VariableDefinition(typename, name)

