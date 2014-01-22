#!/bin/bash

#
# Helper script generate a build environment.
#
# !!! Call the script from within your out-of-source build dir !!!!
#
# author: Martin Hoffmann, Peter Ulbrich
#
#set -x
echo "============================"
echo "Generating Build Environment"
echo "============================"
echo ""

# Get repository base dir from script location
REPODIR=$(dirname $0)/
GENERATOR="Unix Makefiles"

if [ "$2" == "eclipse" ]
then
	GENERATOR="Eclipse CDT4 - Unix Makefiles"
fi

if [ "$2" == "ninja" ]
then
	GENERATOR="Eclipse CDT4 - Ninja"
fi

if [ "$1" == "i386" ]
then
	ARCH=i386
elif [ "$1" == "posix" ]
then
	ARCH=posix
else
	# Default Architecture i386
	ARCH=i386
	echo "Default architecture: $ARCH"
fi

# Call cmake appropriately
if [ $ARCH ]
then
	echo "Setting up build environment [$ARCH]:"
	cmake $REPODIR -DCMAKE_EXPORT_COMPILE_COMMANDS=ON  -DCMAKE_TOOLCHAIN_FILE="$REPODIR/toolchain/$ARCH.cmake" -DCMAKE_BUILD_TYPE=RelWithDebInfo -G "${GENERATOR}"
# We call cmake twice, as the crosscompiler linking does not work otherwise. Don't know why yet..
#	cmake $REPODIR
else
	echo "Currently supported:"
	echo "     * i386"
	echo "     * posix"
	echo "Per default an Eclipse Makefile project file is generated."
	echo "To change to Ninja add 'ninja' as second parameter. (Needs cmake >= 2.8.9 !)"
	echo ""
	echo "Usage: "
	echo "     $0 [i386,posix] <ninja>"
	echo ""
	exit 1
fi

