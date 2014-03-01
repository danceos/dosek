#!/usr/bin/python

import os
import sys
import optparse
import subprocess
from collections import namedtuple

Symbol = namedtuple("Symbol", ["name", "addr", "size", "segment", "type"])

def safe_int(i):
    try:
        return int(i)
    except ValueError:
        return None

def read_symbols(elffile):
    out =  subprocess.check_output(["nm", "-t", "dec", "-S", elffile, "-f", "sysv"])
    ret = []
    for line in out.split("\n"):
        if not "|" in line:
            continue
        line = [x.strip() for x in line.split("|")]
        ret.append(Symbol(name = line[0],
                          addr = safe_int(line[1]),
                          size = safe_int(line[4]),
                          segment = line[6],
                          type = line[3]
                      ))
    return ret

def find_symbol(name):
    for symbol in symbols:
        if name == symbol.name:
            return symbol


if __name__ == "__main__":

    source_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(source_dir, "..")))

    from generator.statistics import Statistics

    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("", "--stats-dict",
                      metavar="STATS_DICT", help="the dict with the statistics")
    parser.add_option("", "--elf",
                      metavar="ELF", help="The elf file")

    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.print_help()
        sys.exit(-1)

    symbols = read_symbols(options.elf)
    stats = Statistics.load(options.stats_dict)

    for abb in stats.find_all("AtomicBasicBlock").values():
        if not 'generated-function' in abb:
            continue
        abb["generated-codesize"] = 0
        for func in abb['generated-function']:
            func = find_symbol(func)
            abb["generated-codesize"] += func.size

    stats.save(options.stats_dict)

