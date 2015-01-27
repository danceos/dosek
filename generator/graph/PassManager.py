import logging
import os
import sys
import time
from generator.graph.AtomicBasicBlock import AtomicBasicBlock
from generator.graph.common import *
from generator.tools import stack

class PassManager:
    def __init__(self, system_graph):
        self.passes = {}
        self.analysis_pipe = []
        self.verifiers = {}
        self.system_graph = system_graph

    def pass_graph(self):
        graph = GraphObjectContainer("PassManager", 'black', root = True)

        ws = stack()

        ws.extend(self.analysis_pipe)
        ws.extend([x for x in self.passes.values() if x.valid])

        passes = {}
        edges = []
        while not ws.isEmpty():
            cur  = ws.pop()
            if not cur in passes:
                passes[cur] = GraphObjectContainer(cur.name(), 'black', 
                                                 data = cur.__doc__)
                graph.subobjects.append(passes[cur])
                for requires in cur.requires():
                    # Requires returns strings
                    requires = self.passes[requires]
                    ws.push(requires)
                    edges.append((cur, requires))


        for edge in edges:
            graph.edges.append(Edge(passes[edge[1]], passes[edge[0]]))

        return graph

    def register_analysis(self, analysis):
        analysis.set_system(self)
        self.passes[analysis.name()] = analysis
        if hasattr(analysis, "pass_alias"):
            self.passes[analysis.pass_alias] = analysis

        # Add to statistics tree
        self.stats.add_child(self, "analysis", analysis)

    def enqueue_analysis(self, analysis):
        if analysis in self.passes:
            analysis = self.passes[analysis]
        assert analysis in list(self.passes.values()), "unregistered pass: %s" % analysis

        if analysis in self.analysis_pipe:
            logging.warning("Pass was enqueued more than once, ignore: %s", analysis)
            return analysis

        self.analysis_pipe.append(analysis)
        return analysis

    def register_and_enqueue_analysis(self, analysis):
        self.register_analysis(analysis)
        self.enqueue_analysis(analysis)

    def read_verify_script(self, path):
        if not path:
            return
        import imp
        old_path = sys.path
        sys.path = sys.path + [os.path.dirname(path)]
        module = imp.load_source('generator.verifier', path)
        sys.path = old_path
        for x in dir(module):
            if x.startswith('after') or x.startswith('before'):
                self.verifiers[x] = getattr(module, x)
        logging.info("Loaded %d verifier functions", len(self.verifiers))

    def get_pass(self, name, only_enqueued=False):
        P = self.passes.get(name, None)
        if only_enqueued and P:
            if P in self.analysis_pipe or P.valid:
                return P
            return None
        return P

    def valid_passes(self):
        ret = set()
        for each in self.passes.values():
            if each.valid:
                ret.add(each)
        return list(ret)

    def analyze(self, basefilename):
        self.basefilename = basefilename
        verifiers_called = set()
        pass_number = 0

        # Dump graph as dot output
        with open("%s_00_passes.dot" % (basefilename), "w+") as fd:
            fd.write(self.pass_graph().dump_as_dot())

        # Dump graph as dot output
        with open("%s_%02d_original.dot" %(basefilename, pass_number), "w+") as fd:
            fd.write(self.system_graph.dump_as_dot())
            pass_number += 1

        while len(self.analysis_pipe) > 0:
            front = self.analysis_pipe[0]
            required = [self.passes[x] for x in front.requires()]
            invalid = [x for x in required if not x.valid]
            if len(invalid) > 0:
                self.analysis_pipe = invalid + self.analysis_pipe
                continue
            # Remove analysis from analysation pipeline
            del self.analysis_pipe[0]
            if front.valid:
                continue
            logging.info("-----")
            # Call before analyzer
            verifier_name = "before_" + front.name()
            if verifier_name in self.verifiers:
                # Disable edge filter for the verifier
                AtomicBasicBlock.set_edge_filter(None)
                self.verifiers[verifier_name](front)
                logging.info(" + %s verifier", verifier_name)
                verifiers_called.add(verifier_name)

            # We promise to only use the specified edge types
            AtomicBasicBlock.set_edge_filter(front.get_edge_filter())

            # Call analyzer pass
            logging.info("PASS: %s", front.name())
            time_before = time.time()
            front.analyze()
            time_delta = time.time() - time_before
            logging.info(" + %.2f seconds", time_delta)
            if hasattr(front, "statistics"):
                front.statistics()

            # Save statistic in stats tree under the analysis
            self.stats.add_data(front, "run-time", time_delta, scalar=True)

            # Check graph integrity
            self.system_graph.fsck()

            # Dump graph as dot output
            with open("%s_%02d_%s.dot" %(basefilename, pass_number, front.name()), "w+") as fd:
                fd.write(self.system_graph.dump_as_dot())

            # Dump analysisgraph as dot output
            if hasattr(front, "dump_as_dot"):
                with open("%s_%02d-pass_%s.dot" %(basefilename, pass_number, front.name()), "w+") as fd:
                    fd.write(front.dump_as_dot())

            # Call afteranalyzer
            verifier_name = "after_" + front.name()
            if verifier_name in self.verifiers:
                # Disable edge filter for the verifier
                AtomicBasicBlock.set_edge_filter(None)
                self.verifiers[verifier_name](front)
                logging.info(" + %s verifier", verifier_name)
                verifiers_called.add(verifier_name)


            pass_number += 1

        # Disable edge filter
        AtomicBasicBlock.set_edge_filter(None)
        with open("%s_%02d_final.dot" %(basefilename, pass_number+1), "w+") as fd:
            fd.write(self.system_graph.dump_as_dot())


