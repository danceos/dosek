import logging
from generator.graph.common import *
from generator.tools import stack

class PassManager:
    def __init__(self):
        self.passes = {}
        self.analysis_pipe = []
        self.verifiers = {}

    def pass_graph(self):
        graph = GraphObjectContainer("PassManager", 'black', root = True)

        ws = stack()

        ws.extend([x.name() for x in self.analysis_pipe])
        for p in self.passes.values():
            if p.valid:
                ws.push(p.name())

        passes = {}

        edges = []
        while not ws.isEmpty():
            p  = ws.pop()
            if not p in passes:
                P = self.passes[p]
                passes[p] = GraphObjectContainer(p, 'black', 
                                                 data = P.__doc__)
                graph.subobjects.append(passes[p])
                for requires in P.requires():
                    ws.push(requires)
                    edges.append((p, requires))


        for edge in edges:
            graph.edges.append(Edge(passes[edge[1]], passes[edge[0]]))

        return graph

    def register_analysis(self, analysis):
        analysis.set_system(self)
        self.passes[analysis.name()] = analysis

    def enqueue_analysis(self, analysis):
        if analysis in self.passes.values():
            self.analysis_pipe.append(analysis)
            return analysis
        elif analysis in self.passes:
            # Analysis name was given
            self.analysis_pipe.append(self.passes[analysis])
            return self.passes[analysis]
        else:
            assert False

    def register_and_enqueue_analysis(self, analysis):
        self.register_analysis(analysis)
        self.enqueue_analysis(analysis)

    def read_verify_script(self, path):
        if not path:
            return
        import imp
        module = imp.load_source('generator.verifier', path)
        for x in dir(module):
            if x.startswith('after') or x.startswith('before'):
                self.verifiers[x] = getattr(module, x)
        logging.info("Loaded %d verifier functions" % len(self.verifiers))

    def get_pass(self, name, only_enqueued = False):
        P = self.passes.get(name, None)
        if only_enqueued:
            if P in self.analysis_pipe or P.valid:
                return P
            return None
        return P

    def analyze(self, basefilename):
        verifiers_called = set()
        pass_number = 0

        # Dump graph as dot output
        with open("%s_passes.dot" %(basefilename), "w+") as fd:
            fd.write(self.pass_graph().dump_as_dot())

        # Dump graph as dot output
        with open("%s_%d_RTSC.dot" %(basefilename, pass_number), "w+") as fd:
            fd.write(self.dump_as_dot())
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
            # Call before analyzer
            verifier_name = "before_" + front.name()
            if verifier_name in self.verifiers:
                self.verifiers[verifier_name](front)
                logging.info("Run %s verifier" % verifier_name)
                verifiers_called.add(verifier_name)

            # Call analyzer pass
            front.analyze()

            # Check graph integrity
            self.fsck()

            # Dump graph as dot output
            with open("%s_%d_%s.dot" %(basefilename, pass_number, front.name()), "w+") as fd:
                fd.write(self.dump_as_dot())

            # Dump analysisgraph as dot output
            if hasattr(front, "dump_as_dot"):
                with open("%s_%d-pass_%s.dot" %(basefilename, pass_number, front.name()), "w+") as fd:
                    fd.write(front.dump_as_dot())

            # Call afteranalyzer
            verifier_name = "after_" + front.name()
            if verifier_name in self.verifiers:
                self.verifiers[verifier_name](front)
                logging.info("Run %s verifier" % verifier_name)
                verifiers_called.add(verifier_name)


            pass_number += 1

