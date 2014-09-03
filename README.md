dOSEK - A Dependability Oriented Static Embedded Kernel
=======================================================

Recent hardware exhibits an increased susceptibility against transient
hardware faults due to shrinking structures sizes and operating
voltages. Automotive safety standards take up this fact, recommending
the deployment of appropriate counter measures. Here, existing
solutions mainly concentrate on the hardening of applications, while
the underlying operating system is often left as unreliable computing
base.

dosek aims to bridge that gap by utilizing consquent design and
implementation concepts for contructing a reliable computing base even
on unreliable hardware. dosek is developed from scratch with
dependability as the first-class design goal Targeting
safety-critical, embedded applications, the system provides an
OSEK/AUTOSAR-conform interface (currently BCC1).

Currently, dOSEK supports three platforms:

- x86: 32-Bit version of dOSEK that runs on bare metal
- posix: 32-Bit version of dOSEK that runs on Linux/x86
- arm: Port to the Panda Board/zedboard (currently WIP)

For more information about the dOSEK concepts, see
    https://www4.cs.fau.de/Research/dOSEK/

Software Requirements
---------------------

    apt-get install binutils-dev build-essential clang-3.4 cmake \
        g++-multilib gcc-multilib git grub-common grub-pc-bin    \
        llvm-3.3-dev llvm-3.3-runtime python-minimal python3     \
        python3-lxml python3-pyparsing python3-pip               \
        qemu-system-x86 xorriso

    LLVM_CONFIG_PATH=/usr/bin/llvm-config-3.3 pip3 install llvmpy

For the ARM version, you will  additionally need

    gcc-arm-none-eabi gdb-arm-none-eabi qemu-system-arm

Building
--------

dOSEK uses cmake as a build system, and therefore supports out of
source builds. To build and run all test-cases you have to type:

    mkdir build; cd build
    ../new_build_env.py
    make build_and_test

To get help about the available targets use

   make help  # long help
   make h     # short help

`after_first_checkout.sh` is only necessary, if you are going to
contribute via our gerrit code review system.

Docker Images
-------------

[![Docker badge](http://docker0.serv.pw:8080/danceos/dosek-base)](https://registry.hub.docker.com/u/danceos/dosek-base/)


We provide a [docker.io](http://www.docker.com) images for a basic
build environment. These images provide an SSH port and access to an
Ubuntu machine that contains all build dependencies. You can either
build the images yourself with

    cd scripts/docker; make
    make run
    make ssh

or you can pull it directly from the docker Hub

    docker pull danceos/dosek-base
    cd scripts/docker; make run; make ssh

In either cases, the password is `dosek`. In the default
configuration, no SSH port will be exposed to the outside world.
