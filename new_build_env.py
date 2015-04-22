#!/usr/bin/python

import os
import sys
import logging
import optparse
import subprocess
import pprint
import config

def setup_logging(log_level):
    """ setup the logging module with the given log_level """

    l = logging.INFO # default
    if log_level == 1:
        l = logging.DEBUG

    logging.basicConfig(level=l)

def cmake_bool(value):
    if value:
        return "ON"
    return "OFF"

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-c', '--clean', dest='CLEAN', action="store_true",
                      default = False,
                      help="Remove all files from current directory before")
    parser.add_option('', '--generator-args', dest='GENERATOR_ARGS', default = "",
                      help="Arguments for the system generator (default: )")
    parser.add_option('-v', '--verbose', dest='verbose', action='count',
                      help="Increase verbosity (specify multiple times for more)")

    parser.add_option('', '--fail-trace-all', dest='FAIL_TRACE_ALL', default = "no",
                      help="Trace all testcases")
    parser.add_option('', '--dependability_failure_logging',
                      dest='DEPFAILLOG', default="no",
                      help="Log checksum calculation interrupts of the dependability service (default: no)")

    del config.model["app"]

    default_config = config.empty_configuration(config.model)
    cmdline_config = config.ConfigurationTree(readonly = False)
    conf_tree = config.into_optparse(config.model, parser, cmdline_config)
    conf = config.ConfigurationTreeStack([default_config, conf_tree], config.model)

    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.print_help()
        sys.exit(-1)

    setup_logging(options.verbose)

    generator_dict = {"make": "Unix Makefiles",
                      "ninja": "Eclipse CDT4 - Ninja",
                      "eclipse": "Eclipse CDT4 - Unix Makefiles"}

    logging.info("Build System: %s", conf.generator)
    logging.info("Arch: %s", conf.arch.self)
    logging.info("Encoded System: %s", conf.dependability.encoded)
    logging.info("MPU Protection: %s", conf.arch.mpu)
    logging.info("Specialized Systemcalls: %s", conf.os.specialize)
    logging.info("State Asserts: %s", conf.dependability.state_asserts)
    logging.info("Symbolic System Execution: %s", conf.os.passes.sse)
    logging.info("Generator Arguments: %s", options.GENERATOR_ARGS)
    logging.info("Fail Trace All: %s", options.FAIL_TRACE_ALL)
    logging.info("Dependability Failure Logging: %s", conf.dependability.failure_logging)


    # Don't think too much about it
    options = eval(str(options))
    toolchain_file = "%(REPODIR)s/toolchain/%(ARCH)s.cmake" % {"ARCH": conf.arch.self,
                                                               "REPODIR": base_dir}
    logging.info("Toolchain File: %s", toolchain_file)

    if options["CLEAN"]:
        logging.info("Removing all files in current directory...")
        subprocess.call("rm * -rf", shell=True)

    with open("config.cmake", "w+") as fd:
        fd.write(config.toCMakeConfig(conf))

    with open("dosek_config.h", "w+") as fd:
        fd.write(config.to_c_header(conf))


    with open("config.dict", "w+") as fd:
        fd.write(pprint.pformat(cmdline_config))

    subprocess.call(["cmake", "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
                     '-DCMAKE_TOOLCHAIN_FILE=%s' % toolchain_file,
                     "-DCMAKE_BUILD_TYPE=Release",
                     "-G", generator_dict[conf.generator],
                     "-DGENERATOR_ARGS='%s'"%options["GENERATOR_ARGS"],
                     "-DFAIL_TRACE_ALL=%s" % options["FAIL_TRACE_ALL"],
                     base_dir])

if __name__ == '__main__':
    main()
