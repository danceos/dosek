from generator.rules.syscalls_full import FullSystemCalls
from generator.elements import CodeTemplate, Include, VariableDefinition, \
    Block, Statement, Comment

from generator.tools import unwrap_seq
from generator.graph.AtomicBasicBlock import E


class SpecializedSystemCalls(FullSystemCalls):
    def __init__(self, global_abb_info):
        FullSystemCalls.__init__(self)
        self.global_abb_info = global_abb_info

    def Comment(self, kernelspace, comment, *args):
        kernelspace.add(Comment(comment % args ))

    def SetReady(self, kernelspace, abb, task):
        abb_info = self.global_abb_info.for_abb(abb)
        # If all currently possible running task abbs are <= prio, we
        # can simply increase the priority
        if abb_info.state_before.is_surely_suspended(task):
            self.Comment(kernelspace, "OPTIMIZATION: We surely know that the task is suspended")
            self.call_function(kernelspace, "scheduler_.SetReadyFromSuspended_impl",
                               "void", [self.task_desc(task)]);
        elif abb_info.state_before.is_surely_ready(task):
            self.Comment(kernelspace, "OPTIMIZATION: Task %s is surely ready, we do not have to activate it.",
                         task)
        else:
            self.call_function(kernelspace, "scheduler_.SetReady_impl",
                               "void", [self.task_desc(task)]);

    def SetSuspended(self, kernelspace, abb, task):
        abb_info = self.global_abb_info.for_abb(abb)
        assert abb_info.state_before.is_surely_ready(task)
        self.call_function(kernelspace, "scheduler_.SetSuspended_impl",
                           "void", [self.task_desc(task)]);

    def Dispatch(self, kernelspace, abb, task):
        abb_info = self.global_abb_info.for_abb(abb)
        if task.name == "Idle":
            self.call_function(kernelspace, "Dispatcher::idle", "void", [])
        else:
            # Check wheter the task is surely continued, or surely started
            is_entry_abb = [task.entry_abb == x for x in abb_info.abbs_after]

            if all(is_entry_abb): # only jumping to an entry abb
                assert len(is_entry_abb) == 1
                self.Comment(kernelspace, "OPTIMIZATION: The task is surely no paused. We can surely start it from scratch.")
                self.call_function(kernelspace, "Dispatcher::StartToTask", "void",
                                   [self.task_desc(task)])
            elif all([not x for x in is_entry_abb]): # Only continuing
                self.Comment(kernelspace, "OPTIMIZATION: The task is surely ready, just resume it.")
                self.call_function(kernelspace, "Dispatcher::ResumeToTask", "void",
                                   [self.task_desc(task)])
            else:
                self.call_function(kernelspace, "Dispatcher::Dispatch", "void",
                                   [self.task_desc(task)])

    def RescheduleTo(self, kernelspace, abb, task):
        """Reschedule to a specific task"""

        # Step 1: Set the current running marker. The current running
        # task is absolutly sure here.
        if abb.function.subtask == task:
            self.Comment(kernelspace, "OPTIMIZATION: We do not have to update the current_task entry")
        elif task.name == "Idle":
            kernelspace.add(Statement("scheduler_.current_task = TaskList::idle_id"))
        else:
            kernelspace.add(Statement("scheduler_.SetCurrentTask(%s)" % self.task_desc(task)))

        # Step 2: Determine the current system priority.
        abb_info = self.global_abb_info.for_abb(abb)
        priorities = set([x.dynamic_priority for x in abb_info.abbs_after])
        if len(priorities) == 1:
            next_prio = unwrap_seq(priorities)
            if next_prio == abb.dynamic_priority:
                self.Comment(kernelspace, "OPTIMIZATION: We do not have to update the current system priority")
            else:
                self.Comment(kernelspace, 
                             "OPTIMIZATION: The system priority is determined."
                             + " Therefore we set it from a constant: %d == %s",
                             next_prio, self.system_graph.who_has_prio(next_prio))
                kernelspace.add(Statement("scheduler_.SetSystemPriority(%d)" % next_prio))
        else:
            # The current system priority is the priority of the next running task
            kernelspace.add(Statement("scheduler_.current_prio = scheduler_.tlist.%s" % task.name))

        # Step 3: Call the dispatcher!
        self.Dispatch(kernelspace, abb, task)


    def ScheduleTargetHint(self, tasks):
        """Returns a SchedulerTargetHint template instanciation for a given
           set of tasks"""
        args = []
        if self.system_graph.get_subtask("Idle") in tasks:
            args.append("true")
        else:
            args.append("false")

        def do(subtask):
            if subtask in tasks:
                args.append("true")
            else:
                args.append("false")

            return ""
        # We use foreach_subtask from BaseRules here, since it is also
        # used in the Scheduler template to build the
        # SchedulerTargetHint C++ template. By this we ensure the right order
        self.foreach_subtask(do)
        return "SchedulerTargetHint<%s>" %( ", ".join(args))


    def Schedule(self, kernelspace, abb):
        if abb.function.subtask.is_isr:
            # OPTIMIZATION: Each ABB is either in an ISR or not,
            # therefore we can surely decide if we have to reschedule
            # in the AST or not
            self.call_function(kernelspace, "request_reschedule_ast",
                               "void", [])
            return

        abb_info = self.global_abb_info.for_abb(abb)
        # All following tasks (Subtask->ABB)
        next_subtasks = abb_info.tasks_after

        if len(next_subtasks) == 1:
            next_subtask = unwrap_seq(next_subtasks.keys())
            self.Comment(kernelspace,
                         "OPTIMIZATION: There is only one possible subtask continuing"
                         + " to, we directly dispatch to that task: %s", next_subtask)
            self.RescheduleTo(kernelspace, abb, next_subtask)
            return


        self.Comment(kernelspace, "OPTIMIZATION: Only the following tasks are possible %s",
                     abb_info.tasks_after.keys())
        schedule_hint = self.ScheduleTargetHint(abb_info.tasks_after.keys())
        self.call_function(kernelspace,
                           "scheduler_.Reschedule< %s >" % (schedule_hint),
                           "void", []);

    def ActivateTask(self, kernelspace, abb):
        subtask = abb.arguments[0]
        abb_info = self.global_abb_info.for_abb(abb)
        if abb_info:
            self.SetReady(kernelspace, abb, subtask)
            self.Schedule(kernelspace, abb)
        else:
            # If we have no information about this systemcall just
            # make a full-featured systemcall
            FullSystemCalls.ActivateTask(self, kernelspace, abb)

    def TerminateTask(self, kernelspace, abb):
        subtask = abb.function.subtask
        abb_info = self.global_abb_info.for_abb(abb)
        if abb_info:
            self.SetSuspended(kernelspace, abb, subtask)
            self.Schedule(kernelspace, abb)
        else:
            # If we have no information about this systemcall just
            # make a full-featured systemcall
            FullSystemCalls.TerminateTask(self, kernelspace, abb)

    def ChainTask(self, kernelspace, abb):
        from_task = abb.function.subtask
        to_task   = abb.arguments[0]
        abb_info = self.global_abb_info.for_abb(abb)
        if abb_info:
            self.SetSuspended(kernelspace, abb, from_task)
            self.SetReady(kernelspace, abb, to_task)
            self.Schedule(kernelspace, abb)
        else:
            # If we have no information about this systemcall just
            # make a full-featured systemcall
            FullSystemCalls.ChainTask(self, kernelspace, abb)

    def ReleaseResource(self, kernelspace, abb):
        from_task = abb.function.subtask
        next_prio = abb.definite_after(E.task_level).dynamic_priority

        abb_info = self.global_abb_info.for_abb(abb)
        if abb_info:
            self.call_function(kernelspace, "scheduler_.SetPriority", "void",
                               [self.task_desc(from_task), str(next_prio)])
            self.call_function(kernelspace, "scheduler_.SetSystemPriority", "void",
                               [str(next_prio)])
            self.Schedule(kernelspace, abb)
        else:
            # If we have no information about this systemcall just
            # make a full-featured systemcall
            FullSystemCalls.ChainTask(self, kernelspace, abb)

