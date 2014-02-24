#!/usr/bin/python

import os, sys
from optparse import OptionParser
from subprocess import *
from tempfile import mkstemp, mkdtemp
import platform
import shutil
import multiprocessing
import signal
import time
import datetime

def parseArgs():
    parser = OptionParser()

    # client options
    parser.add_option("-f", "--fail-client", dest="fail_client",
                      help="FAIL* client to be executed", metavar="CLIENT")
    parser.add_option("-e", "--elf-file", dest="elf_file",
                      help="elf file to be executed", metavar="ELF")
    parser.add_option("-1", "--once", dest="forever", default=True,
                      help="only execute one run and show output", action="store_false")

    # server options
    parser.add_option("-s", "--fail-server", dest="fail_server",
                      help="FAIL* server command to be executed", metavar="SERVER")

    # common options
    parser.add_option("-S", "--fail-server-host", dest="fail_server_host",
                      help="FAIL* server hostname (stats server only on this machine)", metavar="HOST")

    (options, args) = parser.parse_args()

    if not (options.elf_file and options.fail_client):
        parser.error("elf and fail-client are required")

    return options, args

def startServer(options, args):
    # check if this hostname is the server
    if(options.fail_server_host):
        hostname = platform.node()
        if(hostname != options.fail_server_host):
            print "Hostname {} != {}, not starting server".format(hostname, options.fail_server_host)
            return 0

    # run server
    print hostname + ": starting server"
    p = Popen(options.fail_server.split(' '))
    p.wait()

    print hostname + ": server done"
    sys.exit(p.returncode)

def runClient(options, args):
    # setup environment and arguments
    fail_env = os.environ.copy()
    fail_env["FAIL_ELF_PATH"] = options.elf_file
    if(options.fail_server_host):
        fail_env["FAIL_SERVER_HOST"] = options.fail_server_host
    command = [options.fail_client, "-q"] + args

    # working dir = dir of .elf file
    wdir = os.path.dirname(options.elf_file)

    # run client, without output when looping
    if(options.forever):
        fnull = open(os.devnull, 'w')
        p = Popen(command, env=fail_env, cwd=wdir, stdout=fnull, stderr=fnull)
    else:
        p = Popen(command, env=fail_env, cwd=wdir)

    p.wait()
    return p.returncode

def startClients(options, args, i):
    # wait for server to start
    if(options.fail_server):
        time.sleep(3)

    hostname = platform.node()
    print "{}: {}: starting client {}".format(datetime.datetime.now().time().isoformat(), hostname, i)

    if options.forever:
        while True:
            ret = runClient(options, args)
            if ret != 0:
                break
    else:
        ret = runClient(options, args)

    if(ret == 0):
        status = "done"
    else:
        status = "ABORTED"
    print "{}: {}: client {} {}".format(datetime.datetime.now().time().isoformat(), hostname, i, status)
    sys.exit(ret)

def main(options, pargs):
    # how many clients to start
    if options.forever:
        count = multiprocessing.cpu_count()
    else:
        count = 1

    # install SIGINT handler
    signal.signal(signal.SIGINT, signal_handler)

    # processes to start
    processes = []

    # server
    if(options.fail_server):
        p = multiprocessing.Process(target=startServer, name="Server", args=(options, pargs))
        processes.append(p)

    # clients
    for i in xrange(count):
        p = multiprocessing.Process(target=startClients, name="Client "+str(i), args=(options, pargs, i+1))
        processes.append(p)

    # start them all
    for p in processes:
        p.daemon = True
        p.start()

    # wait for completion (or SIGINT)
    for p in processes:
        p.join()
        if(p.name=="Server"):
            sys.exit(0)

def signal_handler(signal, frame):
    print "Terminating!"
    sys.exit(0)

if __name__ == "__main__":
    (options, pargs) = parseArgs()
    main(options, pargs)

