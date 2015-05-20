#!/usr/bin/env python

"""Generate static C++ pagetables from given dOSEK ELF file."""

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
    parser.add_option("", "--config", dest="config",
                      help="place of the config.dict", metavar="CONFIG")


    (options, args) = parser.parse_args()

    default_config = config.empty_configuration(config.model)
    global_config  = config.from_file(options.config)
    options.config = config.ConfigurationTreeStack([default_config, global_config], config.model)

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
    pagedirectory = {};
    max_table_len = 1024
    # iterate allowed regions
    for region in allowed:
        rrange = regions[region.name]
        rrange["mapped"] = True

        # get length and page count
        start = rrange["start"]
        end = rrange["end"]
        assert(start % 4096 == 0)

        length = end - start
        if(length <= 0): continue
        pages_to_place = ((length-1) / 4096)+1

        # page directory/pagetable indices
        pagedir_idx_start = (start & 0xFFC00000) >> 22 # pagedir
        pagetable_idx_start = (start & 0x003FF000) >> 12    # pagetable

        table = pagedirectory.setdefault(pagedir_idx_start, {})

        diridx = pagedir_idx_start
        pidx = pagetable_idx_start
        placed_pages = 0

        while placed_pages < pages_to_place:
            table = pagedirectory.setdefault(diridx, {}) # Get pagetable from directory
            # fill up current table
            while pidx < max_table_len and placed_pages < pages_to_place: # while table has free entries AND we still have to place a page:
                # add page
                table[pidx] = (hex(start+(placed_pages*4096)), str(region.writeable).lower(), str(region.usermode).lower(), region.name,"dir: " + str(diridx) +" pagetableindex: " + str(pidx))
                placed_pages += 1 # one more page placed...
                pidx += 1 # ...and we consumed another entry in the page table
            diridx += 1 # page table is full (or no more pages to place), increment index in page directory
            pidx = 0    # reset page index

    return pagedirectory

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
            for idx in range(1024):
                if idx in table:
                    page = table[idx]
                    f.write("""\t {{ {}, {}, {} }}, // {}  - offset: {}\n""".format(*page))
                else:
                    f.write("\t{},\n")
            f.write("""};\n""")

        # print one pagedirectory
        f.write(PAGEDIR.format(name))
        offset += 4096
        table = 0 # non-empty pagetable number
        for idx in range(1024):
            if idx in pagetables:
                f.write("""\t{{ {}, true }}, // index: {}, ({})\n""".format(hex(start+table*4096), hex(idx), idx))
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
        #print(region)
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
        # Without Privilege Isolation, we have to make the tasks stack
        # and text segment available for the kernel
        if not options.config.arch.privilege_isolation:
            allowed_os += [Region("text_" + task, writeable = False,  usermode = True),
                           Region("stack_" + task, writeable = True, usermode = True)]
            allowed_task[task] += [Region("text_os", writeable = False, usermode = True)]


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
            print( task)
        ptables[task] = generate_pagetables(regions, allowed_task[task])

    write_output(options.cfile, ptables, regions["paging"]["start"])

if __name__ == "__main__":
    source_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(source_dir, "../..")))
    import config

    (options, pargs) = parseArgs()
    main(options, pargs)
