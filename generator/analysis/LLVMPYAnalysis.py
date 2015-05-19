import sys
import re
from functools import reduce
import subprocess
from collections import defaultdict, namedtuple
from .Analysis import Analysis
from .Function import Function
from .Subtask import Subtask
from .AtomicBasicBlock import S, E, ControlFlowEdge
import logging
from .common import Node, Edge, EdgeType, NodeType


class LLVMPYAnalysis(Analysis):
    """ Generate an ABB graph from LLVM intermediate code (.ll) """
    def __init__(self, extractor, files, mergedoutput):
        super(LLVMPYAnalysis, self).__init__()
        self.extractor  = extractor
        self.files      = files
        self.outputfile = mergedoutput

    def requires(self):
        return ["read-oil"]

    pass_alias = "llvmpy"

    def do(self):
        """ Constructor links all files together and produces an ABB graph representation """
        if len(self.files) > 10:
            logging.info("reading %d .ll files", len(self.files))
        else:
            logging.info("reading %s", self.files)

        self.__run_extractor()
        self.__construct_cfg()

    def __run_extractor(self):
        # type If the flag CONFIG_OS_IGNORE_INTERRUPT_SYSCALLS
        # is set, we make all interrupt control system
        # calls to computation blocks.
        self.syscalls = {x for x in S.all() if x != "computation"}
        if self.system_graph.conf.os.ignore_interrupt_systemcalls:
            self.syscalls -= {x.name for x in S.subclass.interrupt_control}

        extractor_args = [self.extractor]
        extractor_args += list(self.files)
        extractor_args += ["-o", self.outputfile]
        structure_file = self.outputfile + ".structure"
        extractor_args += ["-O", structure_file]
        for syscall in self.syscalls:
            extractor_args += ["-s", "OSEKOS_" + syscall]
        subprocess.check_call(extractor_args)

        with open(structure_file) as fd:
            self.structure = eval(fd.read())


    def __construct_cfg(self):
        """ Construct the CFG from the result of the extractor """

        # We use this sort prefix for dicts to make the ABB naming more deterministic
        SORT = lambda x: sorted(x.items(), key = lambda y:y[0])

        abbs = {}
        for func_name, func_struct in SORT(self.structure):
            function = self.system_graph.find(Function, func_name)
            if function == None:
                # Not existing yet, just add it...
                function = Function(func_name)
                self.system_graph._functions[func_name] = function

            # Create Atomic Basic Blocks
            for bb_name, bb_struct in SORT(func_struct):
                if not bb_name.startswith("BB"):
                    continue
                abb = self.system_graph.new_abb([bb_name])
                assert not bb_name in abbs
                abbs[bb_name] = abb
                function.add_atomic_basic_block(abb)

                # Block contains a call
                if "call" in bb_struct:
                    callee = bb_struct["call"]
                    # System Call?
                    m = re.match("OSEKOS_([^_]*)_.*", bb_struct["call"])
                    if m and m.group(1) in self.syscalls:
                        abb.make_it_a_syscall(S.fromString(m.group(1)), bb_struct["arguments"])
            # Entry ABB
            function.set_entry_abb(abbs[func_struct["entry"]])
            # CFG Connections
            for bb_name, bb_struct in func_struct.items():
                if not bb_name.startswith("BB"):
                    continue
                for bb_next_name in bb_struct["successors"]:
                    src = abbs[bb_name]
                    dst = abbs[bb_next_name]
                    src.add_cfg_edge(dst, E.function_level)


            # Remove Dangling Blocks that have no incoming blocks
            # edges, but aren't the entry block. It seems llvm does
            # generate such blocks.
            for abb in function.abbs:
                if len(abb.get_incoming_nodes(E.function_level)) == 0 \
                   and abb != function.entry_abb:
                    function.remove_abb(abb)

        # Find all return blocks for functions
        for function in self.system_graph.functions:
            ret_abbs = []
            for abb in function.abbs:
                if len(abb.get_outgoing_edges(E.function_level)) == 0:
                    ret_abbs.append(abb)

            if len(ret_abbs) == 0:
                logging.info("Endless loop in %s", function)
            elif len(ret_abbs) > 1:
                # Add an artificial exit block
                abb = self.system_graph.new_abb()
                function.add_atomic_basic_block(abb)
                for ret in ret_abbs:
                    ret.add_cfg_edge(abb, E.function_level)
                function.set_exit_abb(abb)
            else:
                function.set_exit_abb(ret_abbs[0])

            if isinstance(function, Subtask) and function.conf.is_isr:
                if not function.exit_abb or not function.exit_abb.isA(S.iret):
                    # All ISR function get an additional iret block
                    iret = self.system_graph.new_abb()
                    function.add_atomic_basic_block(iret)
                    iret.make_it_a_syscall(S.iret, [function])
                    function.exit_abb.add_cfg_edge(iret, E.function_level)
                    function.set_exit_abb(iret)

        # Gather all called Functions in the ABBs, this has to be done, after all ABBs are present
        for func_struct in self.structure.values():
            for bb_name, bb_struct in func_struct.items():
                if not bb_name.startswith("BB"):
                    continue

                # Block contains a call
                if "call" in bb_struct:
                    callee = bb_struct["call"]
                    abbs[bb_name].directly_called_function_name = callee
                    callee = self.system_graph.find(Function, callee)
                    if callee:
                        abbs[bb_name].directly_called_function = callee
                        abbs[bb_name].function.called_functions.add(callee)
