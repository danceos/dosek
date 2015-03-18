#!/usr/bin/env python3

"""
    @defgroup generator The code generator framework
    @{
    These scripts cook our system.
    @}
"""

"""
    @file
    @ingroup generator
    @brief Main entry point
"""
import os
import re
import sys
import logging
import optparse


def split_lls_callback(option, opt, value, parser):
    x = value.split(',')
    y = getattr(parser.values, option.dest)
    if y is not None:
        x = y + x
    setattr(parser.values, option.dest, x)


def setup_logging(log_level):
    """ setup the logging module with the given log_level """

    l = logging.INFO  # default
    if log_level >= 1:
        l = logging.DEBUG

    logging.basicConfig(level=l)
    logging.addLevelName( logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
    logging.addLevelName( logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))

if __name__ == "__main__":

    source_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(source_dir, "..")))

    from generator import Generator
    from generator.analysis import *
    from generator.transform import *
    from generator.coder import *
    from generator.tools import panic, wrap_typecheck_functions

    # Install the typechecking
    wrap_typecheck_functions()

    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("", "--system-desc",
                      metavar="SYSTEM_DESC", help="the system description file (.xml or .oil)")
    parser.add_option("-p", "--prefix",
                      metavar="DIR", help="where to place the dosek source (prefix)")
    parser.add_option("-n", "--name",
                      metavar="STRING", help="system name")
    parser.add_option("-a", "--arch",
                      metavar="STRING", help="for which dosek architecture?")
    parser.add_option('-v', '--verbose', dest='verbose', action='count',
                      help="increase verbosity (specify multiple times for more)",
                      default = 0)
    parser.add_option('', '--template-base',
                      help="Where to search for code templates")
    parser.add_option('', '--verify', dest='verify', default = None,
                      help="verify script for the analysis results")
    parser.add_option('', '--unencoded', dest='unencoded', default = None,
                      help="generate unencoded system",
                      action="store_true")

    parser.add_option('', '--specialize-systemcalls', dest='systemcalls',
                      action="store_const", const = "specialized",
                      help="generate specialized systemcalls")

    parser.add_option('', '--system-calls', dest='systemcalls', default = "full",
                      action="store",
                      help="What kind of system call implementation is desired?")

    
    parser.add_option('-f', '--add-pass', dest='additional_passes', default = [],
                      action="append",
                      help="additional passes (can also be given by setting SGFLAGS)")
    parser.add_option('-D', '', dest='code_options', default = [],
                      action="append",
                      help="additional options passed to the generator")
    parser.add_option('-s', '--source-bytecode', dest='llfiles',
                      action="callback", type='string', callback=split_lls_callback,
                      help="Analyze .ll files. (Comma separated list of files)")
    parser.add_option("-m", "--merged-bytecode", dest='mergedoutput',
                      metavar="DIR", help="output file of the merged system .ll files")

    # Read additional flags from environment variable SGFLAGS
    if "SGFLAGS" in os.environ:
        sys.argv.extend(re.split("[ \t:;,]+", os.environ["SGFLAGS"]))

    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.print_help()
        sys.exit(-1)

    setup_logging(options.verbose)
    graph = SystemGraph(options.code_options)
    graph.add_system_objects()
    pass_manager = graph
    pass_manager.read_verify_script(options.verify)

    if options.system_desc:
        if options.system_desc.lower().endswith(".xml"):
            panic("RTSC XMLs no longer supported")
        elif options.system_desc.lower().endswith(".oil"):
            read_oil = OILReadPass(options.system_desc)
            pass_manager.register_analysis(read_oil)
        else:
            print("No valid system description file")
            parser.print_help()
            sys.exit(-1)
    else:
        print("No system description file passed")
        parser.print_help()
        sys.exit(-1)

    if options.llfiles and len(options.llfiles) > 0:
        mergedoutfile = open(options.mergedoutput, 'w')
        if not mergedoutfile:
            print("Cannot open", options.mergedoutput, "for writing")
            sys.exit(1)
        llvmpy_analysis = LLVMPYAnalysis(options.llfiles, mergedoutfile)
        pass_manager.register_analysis(llvmpy_analysis)

    else:
        print("No .ll files given")
        sys.exit(-1)


    # Ensure that each system call is surrounded by computation blocks
    pass_manager.register_analysis(EnsureComputationBlocks())

    # Find function relevant system calls and merge blocks
    pass_manager.register_analysis(ABBMergePass())

    # Constructing the task_level control flow graph
    pass_manager.register_analysis(AddFunctionCalls())

    # Task-Level: RunningSubtaskInformation
    pass_manager.register_analysis(CurrentRunningSubtask())
    pass_manager.register_analysis(MoveFunctionsToTask())

    # Task-level: Enable/Disable IRQ control
    pass_manager.register_analysis(InterruptControlAnalysis())

    # Task-Level: Dynamic Priority spreading pass
    pass_manager.register_analysis(PrioritySpreadingPass())
    pass_manager.register_analysis(DynamicPriorityAnalysis())

    # System-Level: Analysis
    pass_manager.register_analysis(SystemStateFlow())
    pass_manager.register_analysis(SymbolicSystemExecution())
    pass_manager.register_analysis(ConstructGlobalCFG())

    # System-Level: Exploitation
    pass_manager.register_analysis(DominanceAnalysis())
    pass_manager.register_analysis(CFGRegions())
    pass_manager.register_analysis(GenerateAssertionsPass())

    pass_manager.register_analysis(FiniteStateMachineBuilder())

    # Statistics modules
    pass_manager.register_analysis(GlobalControlFlowMetric("%s/%s_metric" % (options.prefix, options.name)))

    if options.arch == "i386":
        arch_rules = X86Arch()
    elif options.arch == "ARM":
        arch_rules = ARMArch()
    elif options.arch == "posix":
        arch_rules = PosixArch()
    else:
        panic("Unknown --arch=%s", options.arch)

    if options.unencoded:
        os_rules = UnencodedOS()
    else:
        os_rules = EncodedOS()

    assert options.systemcalls in ("full", "specialized", "fsm")

    if options.systemcalls == "specialized":
        # Only when we want to specialize the system calls, run the
        # System-Level analyses
        pass_manager.enqueue_analysis("SymbolicSystemExecution")
        pass_manager.enqueue_analysis("SystemStateFlow")

        global_cfg = pass_manager.enqueue_analysis("ConstructGlobalCFG")
        global_abb_information = global_cfg.global_abb_information_provider()
        logging.info("Global control flow information is provided by %s",
                     global_abb_information.name())
        syscall_rules = SpecializedSystemCalls(global_abb_information)
    elif options.systemcalls == "fsm":
        pass_manager.enqueue_analysis("fsm")
        syscall_rules = FSMSystemCalls()
    else:
        pass_manager.enqueue_analysis("DynamicPriorityAnalysis")
        pass_manager.enqueue_analysis("InterruptControlAnalysis")
        syscall_rules = FullSystemCalls()

    # From command line
    additional_passes = options.additional_passes

    for each in additional_passes:
        P = pass_manager.get_pass(each)
        if not P:
            panic("No such compiler pass: %s", each)
        pass_manager.enqueue_analysis(P)

    pass_manager.analyze("%s/gen_" % (options.prefix))

    generator = Generator.Generator(graph, options.name,
                                    arch_rules,
                                    os_rules,
                                    syscall_rules,
                                    options.code_options)

    generator.template_base = options.template_base
    generator.generate_into(options.prefix)

    graph.stats.save(options.prefix + "/stats.dict.py")
