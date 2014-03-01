from generator.graph.Analysis import Analysis, EnsureComputationBlocks, \
                        FixpointIteraton, MoveFunctionsToTask


class PrioritySpreadingPass(Analysis):
    """This pass reallocated the priorities in the way, that every
       resource has a +1 priority to every task allocating the
       resource and no task has that priority.

    """
    def __init__(self):
        Analysis.__init__(self)
        self.prio_to_participant = {}

    def requires(self):
        return []

    def do(self):
        # Get list of all subtasks
        subtasks = self.system_graph.get_subtasks()

        # Resources and priorities take part in the priority protocol
        participants = [[x.static_priority * 2, x] for x in subtasks]
        for resource in self.system_graph.resources.values():
            prio = 2*max([x.static_priority for x in resource.subtasks]) + 1
            participants.append( [prio, resource] )

        # Sort by priority
        participants = sorted(participants, key = lambda x: x[0])

        # Now there are holes in the priority arrangement, compactify
        # them and set the static priorities
        prio = 0
        for p in participants:
            p[0] = prio
            p[1].static_priority = prio
            self.prio_to_participant[prio] = p[1]
            prio += 1

        assert participants[0][1] == self.system_graph.get_subtask("Idle")
