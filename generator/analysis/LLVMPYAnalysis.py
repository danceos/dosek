import llvm
import llvm.core
import sys
from functools import reduce
from llvmpy import api
from collections import defaultdict, namedtuple
from .Analysis import Analysis
from .Function import Function
from .Subtask import Subtask
from .AtomicBasicBlock import S, E, ControlFlowEdge
import logging
from .common import Node, Edge, EdgeType, NodeType


class LLVMPYAnalysis(Analysis):
    """ Generate an ABB graph from LLVM intermediate code (.ll) """
    def __init__(self, files, mergedoutput):
        super(LLVMPYAnalysis, self).__init__()
        self.files = files
        self.outputfile    = mergedoutput

    def requires(self):
        return ["read-oil"]

    pass_alias = "llvmpy"

    def do(self):
        """ Constructor links all files together and produces an ABB graph representation """
        if len(self.files) > 10:
            logging.info("reading %d .ll files", len(self.files))
        else:
            logging.info("reading %s", self.files)
        self.source_module = self.__combine_source_modules(self.files)
        self.__split_basic_blocks_at_calls()
        self.__add_kickoff_to_subtask_entries()
        # Build a dict with key: function, value: list of BBs
        self.__functions = self.__transform()
        self.__setupCFG()
        self.__add_basic_blocks()

        # Write out source_module
        print(self.source_module, file=self.outputfile)

    @property
    def functions(self):
        """ Returns a dictionary having a function as key, and a list of BBs as value """
        return self.__functions

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
        for idx in range(1, len(source_modules)):
            source_modules[0].link_in(source_modules[idx])
        return source_modules[0]

    def __add_kickoff_to_subtask_entries(self):
        """ Add a call to kickoff at each entry of a user (sub)task """
        int_ty  = llvm.core.Type.int(32) # llvmpy was picky on generating 'void'
        func_ty = llvm.core.Type.function(int_ty, [int_ty])

        kickoff = llvm.core.Function.new(self.source_module, func_ty, "kickoff")

        arg = llvm.core.Constant.int(int_ty, 0)
        # Traverse list of subtasks from the systemdescription
        for st in self.system_graph.subtasks:
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

    def __add_basic_blocks(self):
        graph = self.system_graph

        # Gather functions
        for llvmfunc,llvmbbs in self.functions.items():
            function = graph.find(Function, llvmfunc.name)
            if function == None:
                # Not existing yet, just add it...
                function = Function(llvmfunc.name)
                graph._functions[llvmfunc.name] = function

            # Add llvm function object
            function.set_llvm_function(llvmfunc)
            # Add ABBs
            for bb in llvmbbs:
              abb = graph.new_abb([bb])

              function.add_atomic_basic_block(abb)
              # and set entry abb
              if bb.llvmbb is llvmfunc.entry_basic_block:
                  function.set_entry_abb(abb)

              # type If the flag CONFIG_OS_IGNORE_INTERRUPT_SYSCALLS
              # is set, we make all interrupt control system
              # calls to computation blocks.
              if graph.conf.os.ignore_interrupt_systemcalls:
                  if bb.syscall in [S.DisableAllInterrupts, S.EnableAllInterrupts,
                                    S.SuspendOSInterrupts, S.ResumeOSInterrupts,
                                    S.SuspendAllInterrupts, S.ResumeAllInterrupts]:
                      bb.syscall = S.computation


              # make it a syscall and add arguments
              if bb.is_syscall():
                  abb.make_it_a_syscall(bb.get_syscall(), bb.get_syscall_arguments())
                  # Rename syscall in llvm IR, appending ABB id
                  bb.rename_syscall(abb, self.get_source())

        # Add all implicit intra function control flow graphs
        for func in graph.functions:
            for abb in func.abbs:
                exit_bb = abb.get_exit_bb()
                if not exit_bb:
                    #logging.info("llvmpy_analysis, intra function CFG -> skipping: %s", abb.dump())
                    continue

                nextbbs = exit_bb.get_outgoing_nodes(E.basicblock_level)
                for bb in nextbbs:
                    nextabb = bb.get_parent_ABB()
                    abb.add_cfg_edge(nextabb, E.function_level)
            # Remove Dangling Blocks that have no incoming blocks
            # edges, but aren't the entry block. It seems llvm does
            # generate such blocks.
            for abb in func.abbs:
                if len(abb.get_incoming_nodes(E.function_level)) == 0 \
                   and abb != func.entry_abb:
                    func.remove_abb(abb)

        # Find all return blocks for functions
        for function in graph.functions:
            ret_abbs = []
            for abb in function.abbs:
                if len(abb.get_outgoing_edges(E.function_level)) == 0:
                    ret_abbs.append(abb)

            if len(ret_abbs) == 0:
                logging.info("Endless loop in %s", function)
            elif len(ret_abbs) > 1:
                # Add an artificial exit block
                abb = graph.new_abb()
                function.add_atomic_basic_block(abb)
                for ret in ret_abbs:
                    ret.add_cfg_edge(abb, E.function_level)
                function.set_exit_abb(abb)
            else:
                function.set_exit_abb(ret_abbs[0])

            if isinstance(function, Subtask) and function.conf.is_isr:
                if not function.exit_abb or not function.exit_abb.isA(S.iret):
                    # All ISR function get an additional iret block
                    iret = graph.new_abb()
                    function.add_atomic_basic_block(iret)
                    iret.make_it_a_syscall(S.iret, [function])
                    function.exit_abb.add_cfg_edge(iret, E.function_level)
                    function.set_exit_abb(iret)

        # Gather all called Functions in the ABBs, this has to be done, after all ABBs are present
        for abb in graph.abbs:
            called_funcs = set()
            # Visit all BBs and gather all called Functions
            for bb in abb.get_basic_blocks():
                if bb.calls_function():
                    callee = graph.find(Function, bb.calledFunc.name)
                    if callee:
                        called_funcs.add(callee)
                        abb.called_functions.add(callee)
            # Populate function level set of called functions, needed in ABBMergePass
            abb.function.called_functions.update(called_funcs)



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

    def __extract_event_operand(self, argument):
        if hasattr(argument, "z_ext_value"):
            # If an integer is given
            return [argument.z_ext_value]
        elif argument.opcode == llvm.core.OPCODE_LOAD:
            x = argument.operands[0].name
            return [x]
        elif argument.opcode == llvm.core.OPCODE_OR:
            arg0 = self.__extract_event_operand(argument.operands[0])
            arg1 = self.__extract_event_operand(argument.operands[1])
            return arg0 + arg1
        assert False, "We cannot extract the Event Mask statically"

    def __extract_system_object_operand(self, argument):
        if type(argument) in (list, tuple, str):
            return argument
        if hasattr(argument, "opcode") and argument.opcode == llvm.core.OPCODE_LOAD:
            x = argument.operands[0].name
            return x
        return None

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
                        # Copy the List
                        args = list(inst.operands[0:-1])
                        # Extract the Event arguments
                        if self.syscall in (S.WaitEvent, S.ClearEvent, S.GetEvent):
                            args[0] = self.__extract_event_operand(args[0])
                        if self.syscall in (S.SetEvent,):
                            args[1] = self.__extract_event_operand(args[1])

                        for op in args:
                            opstring = self.__extract_system_object_operand(op)
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


