#!/usr/bin/python

import os, sys
from optparse import OptionParser
from subprocess import *
import shutil

def parseArgs():
    parser = OptionParser()

    parser.add_option("-w", "--workspace", dest="workspace",
                      help="git workspace directory", metavar="WSDIR")
    parser.add_option("-o", "--output", dest="output",
                      help="output git revision file", metavar="GRFILE")
    parser.add_option("-g", "--git", dest="git", default="/usr/bin/git",
                      help="git binary location", metavar="GIT")
    parser.add_option("-f", "--first", dest="check", default=True,
                      help="first run: only write revision file", action="store_false")

    (options, args) = parser.parse_args()

    if not (options.workspace and options.output and options.git):
        parser.error("elf and objdump are required")

    return options, args

def main(options, args):
    # run git describe to get dirty status and hash
    command = [options.git, "describe", "--always", "--dirty"]
    p = Popen(command, stdout=PIPE, cwd=options.workspace)

    (stdout, stderr) = p.communicate(None)
    if p.returncode != 0:
        sys.exit(p.returncode)

    rev = stdout.strip()

    # first run: only write revision file
    if not options.check:
        f = open(options.output, "w")
        f.write(rev + "\n")
        f.close()
        sys.exit(0)

    # check for clean workspace
    if rev.endswith("-dirty"):
        # print error and fail
        print "Your git workspace is not clean!"
        print "Please commit or stash your changes before tracing."
        sys.exit(1)

    # read "old" git hash
    f = open(options.output, "r")
    oldrev = f.read().strip()
    f.close()

    # check for different hash
    if oldrev != rev:
        # different: write new hash
        f = open(options.output, "w")
        f.write(rev + "\n")
        f.close()

        # print error and fail
        print "Git revision changed since last CMake run."
        print "Please re-run build to re-configure CMake."
        sys.exit(1)

    # clean, unchanged git revision, return success
    sys.exit(0)

if __name__ == "__main__":
    (options, pargs) = parseArgs()
    main(options, pargs)

