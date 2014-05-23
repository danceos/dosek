#!/usr/bin/env python3

import llvm
import llvm.core
import sys
from functools import reduce
from llvmpy import api
from collections import defaultdict, namedtuple
from generator.graph.AtomicBasicBlock import S, E, ControlFlowEdge
from generator.graph.common import Node, Edge, EdgeType, NodeType



class BB(Node):

    """ Our own BasicBlock representation, hiding the ugly llvmpy bindings """
    def __init__(self, llvmbb, bb_id):
        Node.__init__(self, ControlFlowEdge, "BB%d" %(bb_id), color="yellow")
        self.llvmbb = llvmbb
        self.successors = self.__find_successors()
        self.syscall = S.fromString("create_computation_type_as_default")
        self.syscallarguments = []
        self.callInst = None
        self.calledFunc = None
        self.__find_syscall()
        self.parent_ABB = None


    def __find_successors(self):
        successors = []
        terminator = self.get_terminator()
        if terminator:
          succnum = terminator.getNumSuccessors()
          for i in range(succnum):
            succ = terminator.getSuccessor(i)
            successors.append(succ)
        return successors

    def __find_syscall(self):
        """ Extract System Call if present in this basic block """
        for inst in self.instructions:
            if type(inst) == llvm.core.CallOrInvokeInstruction:
                calledfunc = inst.called_function
                if calledfunc:
                   self.syscall = S.fromString(calledfunc.name) # Store type
                   self.calledFunc = calledfunc # save called LLVMpy function object
                   self.callInst = inst # save calling LLVMpy instruction
                   if self.is_syscall():
                       for op in inst.operands[0:-1]:
                           opstring = op.name
                           if len(opstring) == 0:
                               opstring = '0'
                           self.syscallarguments.append(opstring)
                   """ Attention: Here we stop at the first found call!
                       This is ok, as we split up every call into a single BB """
                   return

    def rename_syscall(self, abb, source_module):
        """ Rename syscall to a unique name, appending ABB#.
            This has to be done after ABB generation.
        """
        assert not abb == None
        if self.syscall.name == 'StartOS': # StartOS is not renamed
            return
        newname = 'OSEKOS_' + self.syscall.name + '__ABB' + str(abb.id())
        newfun = llvm.core.Function.new(source_module, self.calledFunc._ptr.getFunctionType(), newname)
        self.callInst.called_function = newfun

    def set_parent_ABB(self, parent):
        """ Set parent Atomic Basic Block which includes this basic block """
        self.parent_ABB = parent

    def get_parent_ABB(self):
        """ Returns the Atomic Basic Blocks in which this basic block resides """
        return self.parent_ABB

    def get_call_instruction(self):
        return self.callInst

    def get_called_function(self):
        return self.calledFunc

    def calls_function(self):
        return not self.calledFunc == None

    def is_syscall(self):
        """ Is this basic block actually a system call? """
        return self.syscall.isRealSyscall()

    def get_syscall(self):
        """ Well, returns the system call """
        assert self.is_syscall()
        return self.syscall

    def get_syscall_arguments(self):
        """ Returns a list of system call arguments """
        assert self.is_syscall()
        return self.syscallarguments

    def get_successors(self):
        """ Return a list of succeeding basic blocks """
        return self.successors

    def get_parent(self):
        """ Get the parent llvm basic block """
        return self.llvmbb._ptr.getParent()

    def get_terminator(self):
        """ Get terminating basic block """
        return self.llvmbb._ptr.getTerminator()

    def split_basic_block(self, instruction, newlabel):
        """ Split basic block a the given instruction, adding the label newlabel """
        return api.llvm.BasicBlock.splitBasicBlock(self.llvmbb._ptr, instruction._ptr, newlabel)

    @property
    def instructions(self):
        """ Returns the instructions of the corresponding basic block """
        return self.llvmbb.instructions

    def __str__(self):
        """ The string representation of the basic block in llvm IR syntax """
        return str(self.llvmbb)


class LLVMPYAnalysis:
    """ Generate an ABB graph from LLVM intermediate code (.ll) """
    def __init__(self, files, mergedoutput, systemgraph):
        """ Constructor links all files together and produces an ABB graph representation """
        self.source_module = self.__combine_source_modules(files)
        self.outputfile    = mergedoutput
        self.systemgraph = systemgraph
        self.__split_basic_blocks_at_calls()
        self.__add_kickoff_to_subtask_entries()
        # Build a dict with key: function, value: list of BBs
        self.functiondict = self.__transform()
        self.__setupCFG()


    def writeout_merged_source(self):
        print(self.source_module, file=self.outputfile)


    @property
    def functions(self):
        """ Returns a dictionary having a function as key, and a list of BBs as value """
        return self.functiondict

    def get_source(self):
        """ Returns the LLVMPY source module object """
        return self.source_module

    def __transform(self):
        """ Transform bind LLVM Functions to our own representation """
        bbid = 0
        funcs = defaultdict(list)
        for function in self.source_module.functions:
            for bb in function.basic_blocks:
                mbb = BB(bb, bbid)
                bbid += 1
                funcs[function].append(mbb)
        return funcs


    def __setupCFG(self):
        """ Build the CFG using the llvmpy basic blocks """
        for fname, bbs in self.functions.items():
            blocks = {}
            for basic_block in bbs:
                program_code = str(basic_block.llvmbb)
                assert not program_code in blocks, "Duplicate block contents %s"% program_code
                blocks[program_code] = basic_block

            for basic_block in bbs:
                for successor in basic_block.get_successors():
                    targetbb = blocks[str(successor)]
                    basic_block.add_cfg_edge(targetbb, E.basicblock_level)



    def __combine_source_modules(self, files):
        """ Combine and link all source modules to a single module """
        source_modules = []
        # Load all source modules
        for filename in files:
            source_modules.append(llvm.core.Module.from_assembly(open(filename)))

        # Link them all together
        source_module = reduce(lambda a, b: a.link_in(b), source_modules)
        return source_module

    def __add_kickoff_to_subtask_entries(self):
        """ Add a call to kickoff at each entry of a user (sub)task """
        int_ty  = llvm.core.Type.int(32) # llvmpy was picky on generating 'void'
        func_ty = llvm.core.Type.function(int_ty, [int_ty])

        kickoff = llvm.core.Function.new(self.source_module, func_ty, "kickoff")

        arg = llvm.core.Constant.int(int_ty, 0)
        # Traverse list of subtasks from the systemdescription
        for st in self.systemgraph.get_subtasks():
            if st.is_real_thread(): # omit Alarmhandler. These are generated later.
                # Get corresponding llvmpy function object
                func = self.source_module.get_function_named(st.function_name)
                # Add magic call to kickoff at the beginning
                entrybb = func.entry_basic_block
                # Build a call to magic kickoff routine
                bldr = llvm.core.Builder.new(entrybb)
                bldr.position_at_beginning(entrybb)
                bldr.call(kickoff, [arg], "kickoff_call_%s" % func.name)




    def __split_basic_blocks_at_calls(self):
        """ Splits up the basic blocks at function calls """
        wasCall = False
        for function in self.source_module.functions:
            splitCounter = 0
            for bb in function.basic_blocks:
                instList = bb.instructions
                bb = bb._ptr
                while instList:
                    inst = instList[0]
                    del instList[0]
                    if type(inst) == llvm.core.CallOrInvokeInstruction:
                        wasCall = True

                    if wasCall:
                        bb = api.llvm.BasicBlock.splitBasicBlock(bb,inst._ptr, "%s_split_%d" % (function.name,splitCounter))
                        splitCounter += 1

                    if not type(inst) == llvm.core.CallOrInvokeInstruction:
                        wasCall = False
        #print("Transformed:\n", str(self.source_module))
