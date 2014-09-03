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
    setattr(parser.values, option.dest, value.split(','))

def setup_logging(log_level : int):
    """ setup the logging module with the given log_level """

    l = logging.INFO # default
    if log_level >= 1:
        l = logging.DEBUG

    logging.basicConfig(level=l)

if __name__ == "__main__":

    source_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(source_dir, "..")))

    from generator import LLVMPYAnalysis, Generator, RTSCAnalysis, RTSCSystemDescription, OILSystemDescription
    from generator.rules import *
    from generator.graph import *
    from generator.tools import panic, wrap_typecheck_functions

    # Install the typechecking
    wrap_typecheck_functions()

    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("", "--system-desc",
                      metavar="SYSTEM_DESC", help="the system description file (.xml or .oil)")
    parser.add_option("", "--rtsc-analyze-xml",
                      metavar="RTSC_ANALYZE_XML", help="the RTSC Analyze file")
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
    parser.add_option('', '--specialize-systemcalls', dest='specialize_systemcalls', default = None,
                      action="store_true",
                      help="generate specialized systemcalls")
    parser.add_option('-f', '--add-pass', dest='additional_passes', default = [],
                      action="append",
                      help="additional passes (can also be given by setting SGFLAGS)")
    parser.add_option('-s', '--source-bytecode', dest='llfiles',
                      action="callback", type='string', callback=split_lls_callback,
                      help="Analyze .ll files. (Comma separated list of files)")
    parser.add_option("-m", "--merged-bytecode", dest='mergedoutput',
                      metavar="DIR", help="output file of the merged system .ll files")


    if "SGFLAGS" in os.environ:
        sys.argv.extend(re.split("[ \t:;,]+", os.environ["SGFLAGS"]))

    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.print_help()
        sys.exit(-1)

    setup_logging(options.verbose)
    graph = SystemGraph()
    pass_manager = graph
    pass_manager.read_verify_script(options.verify)

    if options.system_desc:
        if options.system_desc.lower().endswith(".xml"):
            system_description = RTSCSystemDescription.RTSCSystemDescription(options.system_desc)
            graph.read_xml_system_description(system_description)
        elif options.system_desc.lower().endswith(".oil"):
            system_description = OILSystemDescription.OILSystemDescription(options.system_desc)
            graph.read_oil_system_description(system_description)
        else:
            print("No valid system description file")
            parser.print_help()
            sys.exit(-1)
    else:
        print("No system description file passed")
        parser.print_help()
        sys.exit(-1)


    systemanalysis = None

    if options.rtsc_analyze_xml:
      rtsc_analysis = RTSCAnalysis.RTSCAnalysis(options.rtsc_analyze_xml)
      graph.read_rtsc_analysis(rtsc_analysis)
      systemanalysis = rtsc_analysis

    elif options.llfiles and len(options.llfiles) > 0:
        print("Analyzing via llvmpy. ", options.llfiles)
        mergedoutfile = open(options.mergedoutput, 'w')
        if not mergedoutfile:
                print("Cannot open", options.mergedoutput, "for writing")
                sys.exit(1)
        llvmpy_analysis = LLVMPYAnalysis.LLVMPYAnalysis(options.llfiles, mergedoutfile, graph)

        graph.read_llvmpy_analysis(llvmpy_analysis)
        llvmpy_analysis.writeout_merged_source()
        systemanalysis = llvmpy_analysis
        pass_manager.register_and_enqueue_analysis(ABBMergePass())

    else:
        print("Error, choose an analysis variant. RTSC or LLVMPY")
        sys.exit(-1)

    graph.add_system_objects()

    # Ensure that each system call is surrounded by computation blocks
    pass_manager.register_analysis(EnsureComputationBlocks())

    # Constructing the task_level control flow graph
    pass_manager.register_analysis(AddFunctionCalls())

    # Task-Level: RunningSubtaskInformation
    pass_manager.register_analysis(CurrentRunningSubtask())
    pass_manager.register_analysis(MoveFunctionsToTask())

    # Task-level: Enable/Disable IRQ control
    pass_manager.register_and_enqueue_analysis(InterruptControlAnalysis())


    # Task-Level: Dynamic Priority spreading pass
    pass_manager.register_analysis(PrioritySpreadingPass())
    pass_manager.register_and_enqueue_analysis(DynamicPriorityAnalysis())

    # System-Level: Analysis
    pass_manager.register_analysis(SystemStateFlow())
    pass_manager.register_analysis(SymbolicSystemExecution())
    pass_manager.register_analysis(ConstructGlobalCFG())

    # System-Level: Exploitation
    pass_manager.register_analysis(DominanceAnalysis())
    pass_manager.register_analysis(CFGRegions())
    pass_manager.register_analysis(GenerateAssertionsPass())

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
        os_rules = UnencodedSystem()
    else:
        os_rules = EncodedSystem()

    if options.specialize_systemcalls:
        # Only when we want to specialize the system calls, run the
        # System-Level analyses
        pass_manager.enqueue_analysis("SymbolicSystemExecution")
        pass_manager.enqueue_analysis("SystemStateFlow")

        global_cfg = pass_manager.enqueue_analysis("ConstructGlobalCFG")
        global_abb_information = global_cfg.global_abb_information_provider()
        logging.info("Global control flow information is provided by %s",
                     global_abb_information.name())
        syscall_rules = SpecializedSystemCalls(global_abb_information)
    else:
        syscall_rules = FullSystemCalls()

    # From command line
    additional_passes = options.additional_passes

    for each in additional_passes:
        P = pass_manager.get_pass(each)
        if not P:
            panic("No such compiler pass: %s", each)
        pass_manager.enqueue_analysis(P)

    pass_manager.analyze("%s/gen_" % (options.prefix))

    generator = Generator.Generator(graph, options.name, arch_rules,
                                    os_rules,
                                    syscall_rules)

    generator.template_base = options.template_base
    generator.generate_into(options.prefix)

    graph.stats.save(options.prefix + "/stats.dict.py")


