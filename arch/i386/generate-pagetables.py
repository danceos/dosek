#!/usr/bin/python

"""Generate static C++ pagetables from given CoRedOS ELF file."""

import os, sys
from optparse import OptionParser
from subprocess import *
import shutil

## output file header
HEADER = """#include "arch/i386/paging.h"\nusing namespace arch;\n\n"""

## common page directory/table attributes
ATTRIBUTES = """extern "C" const __attribute__ ((aligned (4096))) __attribute__((section(".paging")))"""

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

def generate_pagetables(regions, allowed, supervisor_only, is_supervisor=False):
    """Generate static pagetables from regions"""

    # init dict of pagetables
    pagetables = {};

    # iterate allowed regions
    for rname in allowed:
        rrange = regions[rname]

        # get length and page count
        start = rrange["start"]
        end = rrange["end"]
        length = end - start
        if(length <= 0): continue
        pages = ((length-1) / 4096)+1

        # read-only text pages
        writable = not rname.startswith("text")

        # disallow usermode access to supervisor pages
        usermode = (not rname in supervisor_only)

        # TODO: os functions contained in is_supervisor=True
        # pagetables need userspace access to supervisor pages
        # when run in ring 3
        # so we allow usermode access to all os pages for the kernel
        # page directory, which is used even in ring 3
        # alternative: run os functions in ring 1 or 2
        usermode = usermode or is_supervisor

        # page directory/pagetable indices
        pagetable = (start & 0xFFC00000) >> 22
        offset = (start & 0x003FF000) >> 12

        # get/create empty pagetable as needed
        table = pagetables.setdefault( pagetable, [] )

        # create empty pagetable entries as needed
        for x in range(offset+pages - len(table)):
            table.append(None)

        # insert pagetable entries
        for off in range(pages):
            table[offset+off] = (hex(start+off*4096), str(writable).lower(), str(usermode).lower(), rname)

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

    # regions we are interested in
    allowed_common = ["text_common", "text_fail_allowed", "text", "tss", "data_fail", "data"]
    allowed_os = ["text_os", "stack_os", "ioapic", "lapic"] + allowed_common
    allowed_task = ["text_task{}", "stack_task{}"] + allowed_os
    supervisor_only = ["text_os", "tss", "stack_os", "ioapic", "lapic"]

    ptables = {}
    ptables["os"] = generate_pagetables(regions, allowed_os, supervisor_only, True)
    TASKS = 4 # TODO: from app config
    for task in range(1, TASKS+1):
        ptables["task"+str(task)] = generate_pagetables(regions, [x.format(task) for x in allowed_task], supervisor_only)

    write_output(options.cfile, ptables, regions["paging"]["start"])

if __name__ == "__main__":
    (options, pargs) = parseArgs()
    main(options, pargs)
