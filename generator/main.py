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

import logging

def setup_logging(log_level):
    """ setup the logging module with the given log_level """

    l = logging.WARNING # default
    if log_level == 1:
        l = logging.INFO
    elif log_level >= 2:
        l = logging.DEBUG

    logging.basicConfig(level=l)

if __name__ == "__main__":
    import os, sys
    source_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(source_dir, "..")))

    import optparse
    import SystemDescription
    import RTSCAnalysis
    import ObjectFile
    import Generator
    from generator.rules import *
    from generator.graph import *

    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("", "--system-xml",
                      metavar="SYSTEM_XML", help="the system description file")
    parser.add_option("", "--rtsc-analyze-xml",
                      metavar="RTSC_ANALYZE_XML", help="the RTSC Analyze file")
    parser.add_option("", "--app-object",
                      metavar="APP", help="the application's .o file")
    parser.add_option("", "--nm",
                      metavar="PATH", help="path to an nm binary",
                      default="nm")
    parser.add_option("-o", "--output",
                      metavar="OUTPUT", help="where to place the coredos source")
    parser.add_option('-v', '--verbose', dest='verbose', action='count',
                      help="increase verbosity (specify multiple times for more)")
    parser.add_option('', '--verify', dest='verify',
                      help="verify script for the analysis results")


    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.print_help()
        sys.exit(-1)

    setup_logging(options.verbose)

    system_description = SystemDescription.SystemDescription(options.system_xml)
    app_object = ObjectFile.ObjectFile(options.nm, options.app_object)
    rtsc_analysis = RTSCAnalysis.RTSCAnalysis(options.rtsc_analyze_xml)

    graph = SystemGraph()
    graph.read_verify_script(options.verify)
    graph.read_system_description(system_description)
    graph.read_rtsc_analysis(rtsc_analysis)
    graph.add_system_objects()

    graph.register_and_enqueue_analysis(CurrentRunningSubtask())
    graph.register_and_enqueue_analysis(MoveFunctionsToTask())
    graph.register_and_enqueue_analysis(RunningTaskAnalysis())
    graph.analyze(options.output)


    generator = Generator.Generator(system_description, app_object, rtsc_analysis)
    generator.load_rules(base_rules())
    generator.generate_into(options.output)
