#!/usr/bin/python3

import sys
import os
import optparse

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))
    from config.model  import *
    from config import empty_configuration, into_optparse, check_constraints, from_file

    default_config = empty_configuration(model)

    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-c', '--config',
                      help="Base configuration")

    default_config = empty_configuration(model)
    cmdline_config = ConfigurationTree(readonly = False)
    into_optparse(model, parser, cmdline_config)

    (options, args) = parser.parse_args()

    if options.config:
        global_config  = from_file(options.config)
        conf = ConfigurationTreeStack([default_config, global_config, cmdline_config], model)
    else:
        conf = ConfigurationTreeStack([default_config, cmdline_config], model)

    try:
        check_constraints(constraints, conf, silent = True)
    except:
        sys.exit(1)

