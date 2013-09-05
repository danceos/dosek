#!/bin/bash

BASEDIR=$(dirname $0)

cmake -DCMAKE_TOOLCHAIN_FILE=$BASEDIR/arch/i386/cmake/toolchain.cmake $BASEDIR
