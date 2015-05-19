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
import pprint


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

    import config

    # Install the typechecking
    wrap_typecheck_functions()

    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("", "--system-desc",
                      metavar="SYSTEM_DESC", help="the system description file (.oil)")
    parser.add_option("-p", "--prefix",
                      metavar="DIR", help="where to place the dosek source (prefix)")
    parser.add_option("-c", "--config",
                      metavar="CONF", help="base configuration")
    parser.add_option('-v', '--verbose', dest='verbose', action='count',
                      help="increase verbosity (specify multiple times for more)",
                      default = 0)
    parser.add_option('', '--template-base',
                      help="Where to search for code templates")
    parser.add_option('', '--verify', dest='verify', default = None,
                      help="verify script for the analysis results")
    parser.add_option('-f', '--add-pass', dest='additional_passes', default = [],
                      action="append",
                      help="additional passes (can also be given by setting SGFLAGS)")
    parser.add_option('', '--extractor', dest='extractor',
                      action="store", type='string',
                      help="Analyze .ll files. (Comma separated list of files)")
    parser.add_option('-s', '--source-bytecode', dest='llfiles',
                      action="callback", type='string', callback=split_lls_callback,
                      help="Analyze .ll files. (Comma separated list of files)")
    parser.add_option("-m", "--merged-bytecode", dest='mergedoutput',
                      metavar="DIR", help="output file of the merged system .ll files")

    app_conf_tree = config.into_optparse(config.model, parser)

    # Read additional flags from environment variable SGFLAGS
    if "SGFLAGS" in os.environ:
        sys.argv.extend(re.split("[ \t:;,]+", os.environ["SGFLAGS"]))

    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.print_help()
        sys.exit(-1)

    default_conf = config.empty_configuration(config.model)
    global_conf_tree = config.from_file(options.config)
    conf = config.ConfigurationTreeStack([default_conf, global_conf_tree, app_conf_tree], config.model)

    setup_logging(options.verbose)
    if "VERBOSE" in os.environ:
        setup_logging(3)


    logging.debug(pprint.pformat(conf.as_dict()))
    graph = SystemGraph(conf)
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
        llvmpy_analysis = LLVMPYAnalysis(options.extractor, options.llfiles, options.mergedoutput)
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
    pass_manager.register_analysis(LogicMinimizer())

    # Statistics modules
    pass_manager.register_analysis(GlobalControlFlowMetric("%s/%s_metric" % (options.prefix, conf.app.name)))


    if conf.arch.self == "i386":
        arch_rules = X86Arch()
    elif conf.arch.self == "ARM":
        arch_rules = ARMArch()
    elif conf.arch.self == "posix":
        arch_rules = PosixArch()
    else:
        panic("Unknown --arch=%s", conf.arch.self)

    if conf.dependability.encoded:
        os_rules = EncodedOS()
    else:
        os_rules = UnencodedOS()

    if conf.os.systemcalls == "normal":
        if conf.os.specialize:
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
            pass_manager.enqueue_analysis("DynamicPriorityAnalysis")
            pass_manager.enqueue_analysis("InterruptControlAnalysis")
            syscall_rules = FullSystemCalls()

    elif conf.os.systemcalls == "fsm_pla":
        assert conf.arch.self == "posix", "FSM Encoding is only supported for arch=posix"
        pass_manager.enqueue_analysis("LogicMinimizer")
        pass_manager.enqueue_analysis("fsm")
        syscall_rules = FSMSystemCalls(use_pla = True)
    elif conf.os.systemcalls == "fsm":
        assert conf.arch.self == "posix", "FSM Encoding is only supported for arch=posix"
        pass_manager.enqueue_analysis("fsm")
        syscall_rules = FSMSystemCalls()
    else:
        assert False
    # From command line
    additional_passes = options.additional_passes
    if conf.os.passes.sse:
        additional_passes.append("sse")

    if conf.dependability.state_asserts:
        additional_passes.append("gen-asserts")
    if conf.dependability.cfg_regions:
        additional_passes.append("cfg-regions")


    for each in additional_passes:
        P = pass_manager.get_pass(each)
        if not P:
            panic("No such compiler pass: %s", each)
        pass_manager.enqueue_analysis(P)

    pass_manager.analyze("%s/gen_" % (options.prefix))

    generator = Generator.Generator(graph, conf.app.name,
                                    arch_rules,
                                    os_rules,
                                    syscall_rules,
                                    conf)

    generator.template_base = options.template_base
    generator.generate_into(options.prefix)

    graph.stats.save(options.prefix + "/stats.dict.py")
