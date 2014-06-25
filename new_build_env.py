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
                      help="Architecture (i386|posix)")
    parser.add_option('', '--encoded', dest='ENCODED', default = "yes",
                      help="Build an unencoded system (default: yes)")
    parser.add_option('', '--mpu', dest='MPU', default = "yes",
                      help="Build an unencoded system (default: yes)")
    parser.add_option('', '--specialize', dest='SPECIALIZE', default = "no",
                      help="Use system analysis for specialized system calls (default: no)")
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
                      "eclipse": "Eclipse CDT4 - Unix Makefile"}

    options.GENERATOR = generator_dict[options.GENERATOR]
    options.REPODIR   = base_dir
    options.ENCODED_SYSTEM = cmake_bool(options.ENCODED == "yes")
    options.MPU_PROTECTION = cmake_bool(options.MPU == "yes")
    options.SPECIALIZE_SYSTEMCALLS = cmake_bool(options.SPECIALIZE == "yes")
    options.FAIL_TRACE_ALL = cmake_bool(options.FAIL_TRACE_ALL == "yes")



    logging.info("Build System: %s", options.GENERATOR)
    logging.info("Arch: %s", options.ARCH)
    logging.info("Encoded System: %s", options.ENCODED_SYSTEM)
    logging.info("MPU Protection: %s", options.MPU_PROTECTION)
    logging.info("Specialized Systemcalls: %s", options.SPECIALIZE_SYSTEMCALLS)
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
                     "-DCMAKE_BUILD_TYPE=RelWithDebInfo",
                     "-G", options["GENERATOR"],
                     "-DENCODED_SYSTEM=%s" % options["ENCODED_SYSTEM"],
                     "-DMPU_PROTECTION=%s" % options["MPU_PROTECTION"],
                     "-DSPECIALIZE_SYSTEMCALLS=%s" % options["SPECIALIZE_SYSTEMCALLS"],
                     "-DFAIL_TRACE_ALL=%s" % options["FAIL_TRACE_ALL"],
                     options["REPODIR"]])

if __name__ == '__main__':
    main()
