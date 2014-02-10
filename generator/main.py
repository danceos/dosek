#!/usr/bin/python

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
import sys
import logging
import optparse


def setup_logging(log_level):
    """ setup the logging module with the given log_level """

    l = logging.WARNING # default
    if log_level == 1:
        l = logging.INFO
    elif log_level >= 2:
        l = logging.DEBUG

    logging.basicConfig(level=l)

if __name__ == "__main__":

    source_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(source_dir, "..")))

    from generator import SystemDescription, RTSCAnalysis, Generator
    from generator.rules import *
    from generator.graph import *
    from generator.tools import panic

    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("", "--system-xml",
                      metavar="SYSTEM_XML", help="the system description file")
    parser.add_option("", "--rtsc-analyze-xml",
                      metavar="RTSC_ANALYZE_XML", help="the RTSC Analyze file")
    parser.add_option("-p", "--prefix",
                      metavar="DIR", help="where to place the coredos source (prefix)")
    parser.add_option("-n", "--name",
                      metavar="STRING", help="where to place the coredos source (prefix)")
    parser.add_option("-a", "--arch",
                      metavar="STRING", help="for which coredos architecture?")
    parser.add_option('-v', '--verbose', dest='verbose', action='count',
                      help="increase verbosity (specify multiple times for more)")
    parser.add_option('', '--template-base',
                      help="Where to search for code templates")
    parser.add_option('', '--verify', dest='verify', default = None,
                      help="verify script for the analysis results")


    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.print_help()
        sys.exit(-1)

    setup_logging(options.verbose)

    system_description = SystemDescription.SystemDescription(options.system_xml)
    rtsc_analysis = RTSCAnalysis.RTSCAnalysis(options.rtsc_analyze_xml)

    graph = SystemGraph()
    graph.read_verify_script(options.verify)
    graph.read_system_description(system_description)
    graph.read_rtsc_analysis(rtsc_analysis)
    graph.add_system_objects()

    graph.register_analysis(EnsureComputationBlocks())
    graph.register_analysis(CurrentRunningSubtask())
    graph.register_and_enqueue_analysis(MoveFunctionsToTask())
    graph.register_and_enqueue_analysis(DynamicPriorityAnalysis())
    graph.register_and_enqueue_analysis(RunningTaskAnalysis())
    graph.register_and_enqueue_analysis(GlobalControlFlowMetric("%s/%s_metric" % (options.prefix, options.name)))
    graph.analyze("%s/%s" % (options.prefix, options.name))

    if options.arch == "i386":
        arch = X86Arch();
    elif options.arch == "posix":
        arch = PosixArch()
    else:
        panic("Unknown --arch=%s", options.arch)

    generator = Generator.Generator(graph, options.name, EncodedSystem(), arch)
    generator.template_base = options.template_base
    generator.generate_into(options.prefix)
