#!/usr/bin/python

import os
import sys
import optparse
import subprocess
from collections import namedtuple

Symbol = namedtuple("Symbol", ["name", "addr", "size", "segment", "type"])

def safe_int(i, base=10):
    try:
        return int(i, base)
    except ValueError:
        return None

def read_regions(objdump, elf_file):
    """Read in memory regions from ELF file"""

    # run objdump and get output
    command = [objdump, "-t", elf_file]
    p = Popen(command, stdout=PIPE)

    (stdout, stderr) = p.communicate(None)
    if(p.returncode != 0):
        sys.exit(p.returncode)

    lines = stdout.split('\n')

    # extract all regions:
    # for each region defined by symbols _sregionname, _eregionname
    # create key "regionname" in regions with subkeys start/end pointing to address
    regions = {}
    for l in lines:
        cols = l.split(' ')
        name = cols[-1]
        addr = cols[0]

        if(name.startswith("_s")):
            regions.setdefault(name[2:], {})["start"] = int(addr, 16)

        if(name.startswith("_e")):
            regions.setdefault(name[2:], {})["end"] = int(addr, 16)

    return regions


def read_symbols(elffile, nm = "nm"):
    out =  subprocess.check_output([nm, "-t", "dec", "-C", "-S", "-f", "sysv", elffile])
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

def get_size(symbols, name):
    # symbol size directly from binary?
    for symbol in symbols:
        if name == symbol.name:
            return symbol.size

    # find size through start/end asm markers
    start = 0
    end = 0
    for symbol in symbols:
        if symbol.name.startswith(".asm_label.syscall_start_"+name):
            start = symbol
        if symbol.name.startswith(".asm_label.syscall_end_"+name):
            end = symbol
    if start > 0 and end > 0:
        return end.addr - start.addr
    else:
        #print("no size found for " + name)
        return 0


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
    parser.add_option("", "--nm",
                      metavar="NM", help="The nm program (e.g., i386-elf-nm")

    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.print_help()
        sys.exit(-1)

    if options.nm:
        symbols = read_symbols(options.elf, options.nm)
    else:
        symbols = read_symbols(options.elf)
    stats = Statistics.load(options.stats_dict)

    for abb in stats.find_all("AtomicBasicBlock").values():
        if not 'generated-function' in abb:
            continue
        abb["generated-codesize"] = 0
        for func in abb['generated-function']:
            abb["generated-codesize"] += get_size(symbols, func)

    stats.save(options.stats_dict)

