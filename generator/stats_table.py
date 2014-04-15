#!/usr/bin/python

import os
import sys
import optparse
import subprocess
import re
from collections import namedtuple

def safe_int(i):
    try:
        return int(i)
    except ValueError:
        return None

def subtask_name(name):
    m = re.match("<Subtask (.+)>", name)
    if m:
        return m.group(1)
    else:
        return name

def activation_table(stats, f):
    f.write("subtask\tABB\tactivation\tfunc\tcycles\n")
    for stask in stats.find_all("Subtask").values():
        for abb in stask["abb"]:
            if not 'activations' in abb:
                continue
            i = 0
            for act in abb['activations']:
                i += 1
                for fun in act["trace"]:
                    f.write(subtask_name(stask["_name"]) + "\t" + abb["_name"] + "\t" + str(i) + "\t" + fun[1] + "\t" + str(fun[0])+ "\n")

def codesize_table(stats, f):
    f.write("subtask\tABB\tcodesize\n")
    for stask in stats.find_all("Subtask").values():
        for abb in stask["abb"]:
            if not 'generated-function' in abb:
                continue
            f.write(subtask_name(stask["_name"]) + "\t" + abb["_name"] + "\t" + str(abb["generated-codesize"]) + "\n")

if __name__ == "__main__":
    source_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(source_dir, "..")))

    from generator.statistics import Statistics

    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("", "--stats-dict",
                      metavar="STATS_DICT", help="the dict with the statistics")
    parser.add_option("", "--activations",
                      metavar="ACTIVATIONS", help="output file for activations table")
    parser.add_option("", "--codesize",
                      metavar="CODESIZE", help="output file for activations table")

    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.print_help()
        sys.exit(-1)

    stats = Statistics.load(options.stats_dict)

    activation_file = open(options.activations, "w")
    activation_table(stats, activation_file)
    activation_file.close()

    codesize_file = open(options.codesize, "w")
    codesize_table(stats, codesize_file)
    codesize_file.close()
