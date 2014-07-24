#!/usr/bin/env python

import sys
import os
import subprocess

def pcall(out, arg, sout = None, serr = None, sh = False, mf = False):
    if mf or subprocess.call(arg, stdout = sout, stderr = serr, shell = sh) == 0:
        print("    ( OK ) " + out)
    else:
        print("    (FAIL) " + out)
        sys.exit(1)

if __name__ == "__main__":
    repetitions = 100
    slots = 128
    objects = 64
    try:
        builddir = sys.argv[1]
        outputname = sys.argv[2]
        runs = int(sys.argv[3])
    except:
        print("Parameters: build directory (contents will be removed), output file name (of the log), number of runs")
        sys.exit(1)

    f = open(outputname, "w")
    dn = open(os.devnull, "w")
    depgenroot = os.path.dirname(os.path.abspath(__file__)) + "/"
    os.chdir(builddir)

    print("Prepare")
    pcall("clean build directory", ["rm -r *"], sh = True, mf = True)
    pcall("create dummy application", [depgenroot + "runbench.py", str(repetitions), str(slots), str(objects)], sout = f)
    pcall("create new build environment", [depgenroot + "/../../new_build_env.py", "--dependability_failure_logging=yes"], sout = dn, serr = dn)
    for i in range(0, runs):
        print("Run " + str(i) + ":")
        pcall("create application", [depgenroot + "runbench.py", str(repetitions), str(slots), str(objects)], sout = f)
        pcall("build", ["make", "-j1", "bcc1_depbench"], sout = dn, serr = dn)
        pcall("run", ["qemu-system-i386", "-no-reboot", "-nographic", "-smp", "2", "-kernel", "bcc1_depbench"], sout = f)
