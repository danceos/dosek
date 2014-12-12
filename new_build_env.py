#!/usr/bin/python

import os
import sys
import logging
import optparse
import subprocess

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
    parser.add_option('-g', '--generator', dest='GENERATOR', default = "make",
                      help="CMake Generator (make|ninja|eclipse)")
    parser.add_option('-a', '--arch', dest='ARCH', default = "i386",
                      help="Architecture (i386|ARM|posix)")
    parser.add_option('', '--encoded', dest='ENCODED', default = "yes",
                      help="Build an unencoded system (default: yes)")
    parser.add_option('', '--mpu', dest='MPU', default = "yes",
                      help="Enable memory protection (default: yes)")
    parser.add_option('', '--specialize', dest='SPECIALIZE', default = "no",
                      help="Use system analysis for specialized system calls (default: no)")
    parser.add_option('', '--state-asserts', dest='STATE_ASSERTS', default = "no",
                      help="Generate OS state assertions (default: no)")
    parser.add_option('', '--sse', dest='SSE', default = "no",
                      help="Enable symbolic system execution (default: no)")
    parser.add_option('', '--generator-args', dest='GENERATOR_ARGS', default = "",
                      help="Arguments for the system generator (default: )")
    parser.add_option('', '--fail-trace-all', dest='FAIL_TRACE_ALL', default = "no",
                      help="Trace all testcases")
    parser.add_option('-v', '--verbose', dest='verbose', action='count',
                      help="increase verbosity (specify multiple times for more)")
    parser.add_option('-c', '--clean', dest='CLEAN', action="store_true",
                      default = False,
                      help="remove all files from current directory before")

    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.print_help()
        sys.exit(-1)

    setup_logging(options.verbose)

    generator_dict = {"make": "Unix Makefiles",
                      "ninja": "Eclipse CDT4 - Ninja",
                      "eclipse": "Eclipse CDT4 - Unix Makefiles"}

    options.GENERATOR = generator_dict[options.GENERATOR]
    options.REPODIR   = base_dir
    options.dOSEK_ENCODED_SYSTEM = cmake_bool(options.ENCODED == "yes")
    options.dOSEK_MPU_PROTECTION = cmake_bool(options.MPU == "yes")
    options.dOSEK_SPECIALIZE_SYSTEMCALLS = cmake_bool(options.SPECIALIZE == "yes")
    options.dOSEK_STATE_ASSERTS = cmake_bool(options.STATE_ASSERTS == "yes")
    options.dOSEK_SSE = cmake_bool(options.SSE == "yes")
    options.FAIL_TRACE_ALL = cmake_bool(options.FAIL_TRACE_ALL == "yes")



    logging.info("Build System: %s", options.GENERATOR)
    logging.info("Arch: %s", options.ARCH)
    logging.info("Encoded System: %s", options.dOSEK_ENCODED_SYSTEM)
    logging.info("MPU Protection: %s", options.dOSEK_MPU_PROTECTION)
    logging.info("Specialized Systemcalls: %s", options.dOSEK_SPECIALIZE_SYSTEMCALLS)
    logging.info("State Asserts: %s", options.dOSEK_STATE_ASSERTS)
    logging.info("Symbolic System Execution: %s", options.dOSEK_SSE)
    logging.info("Generator Arguments: %s", options.GENERATOR_ARGS)
    logging.info("Fail Trace All: %s", options.FAIL_TRACE_ALL)


    # Don't think too much about it
    options = eval(str(options))
    toolchain_file = "%(REPODIR)s/toolchain/%(ARCH)s.cmake" % dict(options)
    logging.info("Toolchain File: %s", toolchain_file)

    if options["CLEAN"]:
        logging.info("Removing all files in current directory...")
        subprocess.call("rm * -rf", shell=True)

    subprocess.call(["cmake", "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
                     '-DCMAKE_TOOLCHAIN_FILE=%s' % toolchain_file,
                     "-DCMAKE_BUILD_TYPE=Release",
                     "-G", options["GENERATOR"],
                     "-DdOSEK_ENCODED_SYSTEM=%s" % options["dOSEK_ENCODED_SYSTEM"],
                     "-DdOSEK_MPU_PROTECTION=%s" % options["dOSEK_MPU_PROTECTION"],
                     "-DdOSEK_SPECIALIZE_SYSTEMCALLS=%s" % options["dOSEK_SPECIALIZE_SYSTEMCALLS"],
                     "-DdOSEK_STATE_ASSERTS=%s" % options["dOSEK_STATE_ASSERTS"],
                     "-DdOSEK_SSE=%s" % options["dOSEK_SSE"],
                     "-DGENERATOR_ARGS='%s'"%options["GENERATOR_ARGS"],
                     "-DFAIL_TRACE_ALL=%s" % options["FAIL_TRACE_ALL"],
                     options["REPODIR"]])

if __name__ == '__main__':
    main()
