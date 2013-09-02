#!/bin/bash

BASEDIR=$(dirname $0)

cmake -DCMAKE_TOOLCHAIN_FILE=$BASEDIR/arch/x86/cmake/toolchain.cmake $BASEDIR
