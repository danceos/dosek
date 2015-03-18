from .Analysis import Analysis
from .AtomicBasicBlock import E

class GlobalControlFlowMetric(Analysis):
    def __init__(self, filename):
        Analysis.__init__(self)
        self.filename = filename
    def requires(self):
        # We require all possible system edges to be contructed
        return ["ConstructGlobalCFG"]

    def do(self):
        current_task = self.get_analysis("CurrentRunningSubtask")

        abbs = self.system_graph.abbs
        # All possible directed edges
        all_possible_neighbours_count = 0
        # All edges that go to higher priority blocks or the system blocks
        higher_priority_count = 0
        # Analysed Edges
        analyzed_edges_count = 0
        for source in abbs:
            for target in abbs:
                if source == target:
                    continue
                abb0 = current_task.for_abb(source)
                abb1 = current_task.for_abb(target)
                # System blocks are lost
                if abb0 == None or abb1 == None:
                    continue
                all_possible_neighbours_count += 1
                if abb1.static_priority >= abb0.static_priority:
                    higher_priority_count +=1
                if target in source.get_outgoing_nodes(E.system_level):
                    analyzed_edges_count += 1

        with open(self.filename, "w+") as fd:
            fd.write("%s, %d, %d, %d\n" %( 
                self.filename,
                all_possible_neighbours_count,
                higher_priority_count,
                analyzed_edges_count))


