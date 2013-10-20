#!/usr/bin/python

"""
    @defgroup generator The code generator framework
    @{
    These scripts cook our system.
    @}
"""

"""
    @file
    @ingroup generator
    @brief Main entry point
"""
if __name__ == "__main__":
    import os, sys
    source_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.abspath(os.path.join(source_dir, "..")))

    import optparse
    import SystemDescription
    import ObjectFile
    import Generator
    from generator.rules import *


    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("", "--system-xml",
                      metavar="SYSTEM_XML", help="the system description file")
    parser.add_option("", "--app-object",
                      metavar="APP", help="the application's .o file")
    parser.add_option("", "--nm",
                      metavar="PATH", help="path to an nm binary",
                      default="nm")
    parser.add_option("-o", "--output",
                      metavar="OUTPUT", help="where to place the coredos source")

    (options, args) = parser.parse_args()

    if len(args) > 0:
        parser.print_help()
        sys.exit(-1)

    system_description = SystemDescription.SystemDescription(options.system_xml)
    app_object = ObjectFile.ObjectFile(options.nm, options.app_object)

    generator = Generator.Generator(system_description, app_object)
    generator.load_rules(posix_rules())
    generator.load_rules(base_rules())
    generator.generate_into(options.output)
