#!/usr/bin/python

"""Generate static C++ pagetables from given CoRedOS ELF file."""

import os, sys
from optparse import OptionParser
from collections import namedtuple
from subprocess import *
import shutil
import copy

## output file header
HEADER = """#include "arch/i386/paging.h"\nusing namespace arch;\n\n"""

## common page directory/table attributes
ATTRIBUTES = """extern "C" const __attribute__ ((aligned (4096)))\n   __attribute__((section(".paging")))\n   """

## page table definition
PAGETABLE = ATTRIBUTES + """ PageTableEntry pagetable_{}[1024] = {{\n"""

## page directory definition
PAGEDIR = ATTRIBUTES + """ PageDirectoryEntry pagedir_{}[1024] = {{\n"""

def parseArgs():
    """Parse arguments"""
    parser = OptionParser()

    parser.add_option("-e", "--elf-file", dest="elf_file",
                      help="elf file to extract", metavar="ELF")
    parser.add_option("-o", "--objdump", dest="objdump", default="/usr/bin/objdump",
                      help="objdump binary location", metavar="OBJDUMP")
    parser.add_option("-c", "--c-file", dest="cfile", default="pagetables.cc",
                      help="generated C++ file", metavar="CCFILE")

    (options, args) = parser.parse_args()

    if not (options.elf_file and options.objdump and options.cfile):
        parser.error("elf-file, c-file and objdump are required")

    return options, args

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

Region = namedtuple("Region", ["name", "writeable", "usermode"])

def generate_pagetables(regions, allowed):
    """Generate static pagetables from regions"""

    # init dict of pagetables
    pagetables = {};

    # iterate allowed regions
    for region in allowed:
        rrange = regions[region.name]
#        region_is_mapped(regions, region.name)
        rrange["mapped"] = True

        # get length and page count
        start = rrange["start"]
        end = rrange["end"]
        assert(start % 4096 == 0)

        length = end - start
        if(length <= 0): continue
        pages = ((length-1) / 4096)+1

        # page directory/pagetable indices
        pagetable = (start & 0xFFC00000) >> 22
        offset = (start & 0x003FF000) >> 12

        # get/create empty pagetable as needed
        table = pagetables.setdefault( pagetable, [] )

        # create empty pagetable entries as needed
        for x in range(offset+pages - len(table)):
            table.append(None)

        if "VERBOSE" in os.environ:
            print hex(rrange["start"]), hex(rrange["end"]),  region

        # insert pagetable entries
        for off in range(pages):
            table[offset+off] = (hex(start+off*4096), str(region.writeable).lower(), str(region.usermode).lower(), region.name)

    return pagetables

def write_output(filename, ptables, paging_start):
    """Write C++ output file from pagetables"""

    # open output file and write header
    f = open(filename, "w")
    f.write(HEADER)

    # absolute address of current pagetable/pagedir
    offset = paging_start
    for name, pagetables in iter(sorted(ptables.items())):
        # start of pagetables for this pagedir
        start = offset

        # print all pagetables
        for idx, table in iter(sorted(pagetables.items())):
            offset += 4096
            f.write(PAGETABLE.format(name + "_" + str(idx)))
            for page in table:
                if(page != None):
                    f.write("""\t {{ {}, {}, {} }}, // {}\n""".format(*page))
                else:
                    f.write("\t{},\n")
            f.write("""};\n""")

        # print one pagedirectory
        f.write(PAGEDIR.format(name))
        offset += 4096
        table = 0 # non-empty pagetable number
        for idx in xrange(0, 1023):
            if idx in pagetables:
                f.write("""\t{{ {}, true }},\n""".format(hex(start+table*4096)))
                table += 1
            else:
                f.write("\t{},\n")

        f.write("""};\n""")

    # close file and exit
    f.close()

def main(options, args):
    regions = read_regions(options.objdump, options.elf_file)

    # Collect task names:
    tasks = set()
    for region in regions:
        if region.startswith("text_task"):
            tasks.add (region[len("text_task"):])

    # regions we are interested in
    allowed_common = [ Region("cga"                   , writeable = True , usermode = True),
                       Region("text"                  , writeable = False, usermode = True),
                       Region("text_irqs"             , writeable = False, usermode = False),
                       Region("text_common"           , writeable = False, usermode = True),
                       Region("data"                  , writeable = True,  usermode = True)]

    allowed_os  = copy.deepcopy(allowed_common)
    allowed_os += [  Region("stack_os", writeable = True , usermode  = True),
                     Region("tss"     , writeable = True , usermode  = True),
                     Region("ioapic",   writeable = True , usermode  = True),
                     Region("lapic",    writeable = True , usermode  = True),
                     Region("text_startup", writeable = False, usermode = False),
                     Region("text_os", writeable = False, usermode = True),
                     Region("data_os", writeable = True , usermode = True),
                     Region("data_arch", writeable = True , usermode = True)]


    allowed_task = {}
    for task in tasks:
        task = "task%s" % task
        allowed_task[task] = copy.deepcopy(allowed_common)
        # A Task can additionally read its text segment and write its stack
        allowed_task[task] += [ Region("text_" + task, writeable = False,  usermode = True),
                                Region("data_" + task, writeable = True, usermode = True),
                                Region("stack_" + task, writeable = True, usermode = True),
                                Region("stack_os", writeable = True , usermode  = False),
                                Region("tss"     , writeable = False , usermode = False),
                                Region("lapic",    writeable = True , usermode  = False),
                                Region("ioapic",   writeable = True , usermode  = False),
                                Region("data_os", writeable = False , usermode = True),
                                Region("data_arch", writeable = False , usermode = True)
        ]

    ptables = {}
    ptables["os"] = generate_pagetables(regions, allowed_os)
    for task in allowed_task:
        if "VERBOSE" in os.environ:
            print task
        ptables[task] = generate_pagetables(regions, allowed_task[task])

    write_output(options.cfile, ptables, regions["paging"]["start"])

if __name__ == "__main__":
    (options, pargs) = parseArgs()
    main(options, pargs)
