#!/usr/bin/python

import os, sys
from optparse import OptionParser
from subprocess import *
import shutil

def parseArgs():
    parser = OptionParser()

    parser.add_option("-e", "--elf-file", dest="elf_file",
                      help="elf file to extract", metavar="ELF")
    parser.add_option("-o", "--objdump", dest="objdump", default="/usr/bin/objdump",
                      help="objdump binary location", metavar="OBJDUMP")

    (options, args) = parser.parse_args()

    if not (options.elf_file and options.objdump):
        parser.error("elf and objdump are required")

    return options, args

def writeFile(name, start, end):
    f = open(name, "w")
    f.write("{} {}\n".format(start, end-start))
    f.close()

def main(options, args):
    command = [options.objdump, "-t", options.elf_file]
    p = Popen(command, stdout=PIPE) 

    (stdout, stderr) = p.communicate(None)
    lines = stdout.split('\n')
    
    for l in lines:
    	cols = l.split(' ')
	name = cols[-1]
	addr = cols[0]

	if(cols[-1] == "_stext_fail"):
	    text_start = int(addr, 16)
	if(cols[-1] == "_etext_fail"):
	    text_end = int(addr, 16)
	if(cols[-1] == "_sdata_fail"):
	    data_start = int(addr, 16)
	if(cols[-1] == "_edata_fail"):
	    data_end = int(addr, 16)
	if(cols[-1] == "stack_bottom"):
	    stack_start = int(addr, 16)
	if(cols[-1] == "stack_top"):
	    stack_end = int(addr, 16)

    writeFile("text_map", text_start, text_end)
    writeFile("data_map", data_start, data_end)
    writeFile("stack_map", stack_start, stack_end)

    sys.exit(p.returncode)

if __name__ == "__main__":
    (options, pargs) = parseArgs()
    main(options, pargs)

