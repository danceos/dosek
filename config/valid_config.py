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

    parser.add_option('-e', '--equal',
                      help="Configured values must be equal",
                      action='store_true', default=False)


    default_config = empty_configuration(model)
    cmdline_config = ConfigurationTree(readonly = False)
    into_optparse(model, parser, cmdline_config)

    (options, args) = parser.parse_args()

    if options.config:
        global_config  = from_file(options.config)
        actual_conf = ConfigurationTreeStack([default_config, global_config], model)
        conf = ConfigurationTreeStack([default_config, global_config, cmdline_config], model)

    else:
        actual_conf = ConfigurationTreeStack([default_config], model)
        conf = ConfigurationTreeStack([default_config, cmdline_config], model)

    if options.equal:
        for path, value in cmdline_config:
            actual_value = actual_conf.get(path)[0]
            if actual_value != value:
                sys.exit(1)
        sys.exit(0)

    try:
        check_constraints(constraints, conf, silent = True)
    except:
        sys.exit(1)


