from .Analysis import Analysis
from .OILSystemDescription import OILSystemDescription

from .Task import Task
from .Subtask import Subtask
from .AtomicBasicBlock import AtomicBasicBlock, E, S
from .Function import Function
from .PassManager import PassManager
from .Sporadic import Counter, Alarm, ISR, AlarmSubtask
from .Resource import Resource
from .Event import Event
import logging


class OILReadPass(Analysis):
    pass_alias = "read-oil"

    def __init__(self, oil_file):
        super(OILReadPass, self).__init__()

        self.oil_file = oil_file

    def do(self):
        logging.info("read %s", self.oil_file)
        system_description = OILSystemDescription(self.oil_file)
        self.__read_oil_system_description(system_description)

    def __read_oil_system_description(self, oil):
        """Reads in the system description out of an OIL file and builds the
        tasks and subtask objects and connects them

        """
        graph = self.system_graph
        maxprio = 0  # Maximum task prio according to OIL file
        # We use event_ids that are system wide unique
        event_id = 0

        for task_desc in oil.getTasks():
            # Create or Get the Task (Group)
            task_group = task_desc.taskgroup
            taskname = task_desc.name
            if task_group not in graph._tasks:
                task = Task(graph, task_group)
                graph._tasks[task_group] = task
                graph.stats.add_child(graph, "task", task)
            else:
                task = graph._tasks[task_group]

            subtask = Subtask(graph, taskname, "OSEKOS_TASK_FUNC_" + taskname, task_desc)
            graph._subtasks[taskname] = subtask
            # Every subtask belongs to a task
            task.add_subtask(subtask)
            # Every subtask is also a function
            graph._functions[subtask.function_name] = subtask
            graph.stats.add_child(task, "subtask", subtask)
            # Shift all priorities by +1
            task_desc.static_priority += 1
            assert task_desc.static_priority >= 1, \
                    "No user thread can have the priority 0, reserved for the idle thread"

            if task_desc.static_priority > maxprio:
                maxprio = task_desc.static_priority

            graph.stats.add_data(subtask, "is_isr", False, scalar = True)

            # If basic tasks are not allowed, all tasks become extended tasks
            if not self.system_graph.conf.os.basic_tasks:
                subtask.conf.basic_task = False

            # Instantiate events for the current task
            for event in task_desc.events.values():
                event.used = True
                Ev = Event(graph, "%s__%s"% (subtask.name, event.name), subtask, event_id, event)
                if event.MASK != "AUTO":
                    try:
                        Ev.event_mask = int(event.MASK)
                    except ValueError as Ex:
                        panic("Event Mask not readable: %s", str(Ex))
                    assert len([x for x in bin(Ev.event_mask) if x == "1"]) == 1, \
                        "Exactly one bit must be set in event_mask %s" % Ev


                subtask._events[event.name] = Ev
                subtask.event_mask_valid |= Ev.event_mask
                graph._events[Ev.name] = Ev
                event_id += 1
                assert event_id < 32, "No more than 32 Events"

        # Events: Assert that every event was used at least once
        for event in oil.getEvents():
            assert hasattr(event, "used") and event.used, "Event %s was not used" % event.name

        #  ISR
        isr_prio = maxprio + 1  # ISR get priorities above maximum task prio
        for isr_desc in oil.getISRs():
            task_group = isr_desc.taskgroup
            taskname = isr_desc.name
            if task_group not in graph._tasks:
                task = Task(graph, task_group)
                graph._tasks[task_group] = task
                graph.stats.add_child(graph, "task", task)
            else:
                task = graph._tasks[task_group]

            # Generate Subtask for ISR
            subtask = Subtask(graph, isr_desc.name, "OSEKOS_ISR_" + isr_desc.name,
                              isr_desc)
            graph._subtasks[isr_desc.name] = subtask
            task.add_subtask(subtask)
            graph._functions[subtask.function_name] = subtask
            graph.stats.add_child(task, "subtask", subtask)

            prio = isr_desc.PRIORITY
            if prio == -1:
                prio = isr_prio
                isr_prio = isr_prio + 1 # increment isr prio

            subtask.conf.static_priority = prio
            graph.stats.add_data(subtask, "is_isr", True, scalar=True)

            graph._isrs[isr_desc.name] = ISR(graph, subtask)

        # Now, after all Task (Groups) are created, now we catch the
        # task group configurations.
        for taskgroup_desc in oil.getTaskGroups():
            task_group = graph.get(Task, taskgroup_desc.name)
            task_group.set_promises(taskgroup_desc.promises)

        # Counters
        for conf in oil.getCounters():
            graph._counters[conf.name] = Counter(graph, conf.name, conf)


        # Alarms
        hardware_alarms = []
        for conf in oil.getAlarms():
            conf.subtask = graph.get(Subtask, conf.subtask)
            assert conf.subtask != None, "Alarm does not activate any task! (maybe callback?)"
            conf.event = conf.subtask.find(Event, conf.event)
            conf.counter = graph.get(Counter, conf.counter)

            alarm_object = Alarm(graph, conf)

            # Every hardware alarm carries a oil call
            if conf.counter.conf.softcounter:
                # For softcounters we use an unregistered ABB
                inner_syscall = AtomicBasicBlock(graph)
                graph.stats.add_child(graph, "ABB", inner_syscall)
            else:
                inner_syscall = graph.new_abb()
            if conf.event:
                inner_syscall.make_it_a_syscall(S.SetEvent, [conf.subtask, [conf.event]])
            else:
                inner_syscall.make_it_a_syscall(S.ActivateTask, [conf.subtask])
            alarm_object.carried_syscall = inner_syscall

            # Add it to the list of all alarms, and to the list of hardware alarms
            graph._alarms[alarm_object.name] = alarm_object
            if not conf.counter.conf.softcounter:
                hardware_alarms.append(alarm_object)

        if len(hardware_alarms) > 0:
            # Generate Alarm Checker subtask
            subtask = AlarmSubtask(graph)

            # And add it to the oil task
            graph.system_task.add_subtask(subtask)
            graph.stats.add_child(task, "subtask", subtask)

            # Register Subtask
            graph._functions[subtask.function_name] = subtask
            graph._subtasks[subtask.name] = subtask

            pred_cc = None
            pred_syscall = None
            for alarm_object in sorted(hardware_alarms, key = lambda a: a.conf.subtask.static_priority):
                subtask.alarms.append(alarm_object)

                # Chain to last CheckCounter
                cc = graph.new_abb()
                subtask.add_atomic_basic_block(cc)
                cc.make_it_a_syscall(S.CheckAlarm, [alarm_object])
                if pred_cc:
                    pred_cc.add_cfg_edge(cc, E.function_level)
                    pred_syscall.add_cfg_edge(cc, E.function_level)
                else:
                    subtask.set_entry_abb(cc)

                subtask.add_atomic_basic_block(alarm_object.carried_syscall)
                cc.add_cfg_edge(alarm_object.carried_syscall, E.function_level)
                pred_cc, pred_syscall = cc, alarm_object.carried_syscall

            iret = graph.new_abb()
            subtask.add_atomic_basic_block(iret)
            iret.make_it_a_syscall(S.iret, [subtask])
            subtask.set_exit_abb(iret)
            pred_cc.add_cfg_edge(iret, E.function_level)
            pred_syscall.add_cfg_edge(iret, E.function_level)

            graph.AlarmHandlerSubtask = subtask
        else:
            # No hardware alarms
            graph.AlarmHandlerSubtask = None

        #  Resources
        for res in oil.getResources():
            subtasks = [graph.get(Subtask, x) for x in res.tasks]
            graph._resources[res.name] = Resource(graph, res.name, subtasks, res)

        if graph.find(Resource, "RES_SCHEDULER") is None:
            sched = "RES_SCHEDULER"
            class ResourceConfig:
                def __init__(self):
                    self.static_priority = None

            subtasks = [x for x in graph.subtasks if not x.conf.is_isr]
            graph._resources[sched] = Resource(graph, sched, subtasks, ResourceConfig())

        for obj in oil.getCheckedObjects():
            graph._checkedObjects[obj.name] = obj


