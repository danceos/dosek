#!/bin/bash

# settings
START_DIR=`pwd`
BUILD_DIR=`pwd`/build
SOURCE_DIR=`pwd`/..

# arguments
if [ $1 == "--mpu-only" ]; then
  echo "Skipping no-mpu variants"
  MPUONLY=1
  BENCHMARKS=${@:2}
else
  MPUONLY=0
  BENCHMARKS=$@
fi

rm -rf $BUILD_DIR
mkdir $BUILD_DIR

# ENCODED, MPU
mkdir $BUILD_DIR/x86-encoded-mpu
cd $BUILD_DIR/x86-encoded-mpu

$SOURCE_DIR/new_build_env.py -a i386 --encoded yes --mpu yes

for BENCH in $BENCHMARKS
do
make fail-$BENCH-regs
make fail-$BENCH-mem
make fail-$BENCH-ip

VARIANT=CoRedOS-`cat fail-$BENCH/.gitrev`
objdump -wC -t -j .data -j .text fail-$BENCH/fail-$BENCH > $START_DIR/$VARIANT-$BENCH-encoded-mpu.syms
cp fail-$BENCH/fail-$BENCH $START_DIR/$VARIANT-$BENCH-encoded-mpu.elf
find . -iname stats.dict.py -exec cp '{}' $START_DIR/$VARIANT-$BENCH-encoded-mpu-stats.dict.py \;
done


# ENCODED, NOMPU
if [ $MPUONLY == 0 ]; then
mkdir $BUILD_DIR/x86-encoded-nompu
cd $BUILD_DIR/x86-encoded-nompu

$SOURCE_DIR/new_build_env.py -a i386 --encoded yes --mpu no

for BENCH in $BENCHMARKS
do
make fail-$BENCH-regs-nompu
make fail-$BENCH-mem-nompu
make fail-$BENCH-ip-nompu

objdump -wC -t -j .data -j .text fail-$BENCH/fail-$BENCH > $START_DIR/$VARIANT-$BENCH-encoded-nompu.syms
cp fail-$BENCH/fail-$BENCH $START_DIR/$VARIANT-$BENCH-encoded-nompu.elf
find . -iname stats.dict.py -exec cp '{}' $START_DIR/$VARIANT-$BENCH-encoded-nompu-stats.dict.py \;
done
fi


# UNENCODED, MPU
mkdir $BUILD_DIR/x86-unencoded-mpu
cd $BUILD_DIR/x86-unencoded-mpu

$SOURCE_DIR/new_build_env.py -a i386 --encoded no --mpu yes

for BENCH in $BENCHMARKS
do
make fail-$BENCH-regs-unencoded
make fail-$BENCH-mem-unencoded
make fail-$BENCH-ip-unencoded

objdump -wC -t -j .data -j .text fail-$BENCH/fail-$BENCH > $START_DIR/$VARIANT-$BENCH-unencoded-mpu.syms
cp fail-$BENCH/fail-$BENCH $START_DIR/$VARIANT-$BENCH-unencoded-mpu.elf
find . -iname stats.dict.py -exec cp '{}' $START_DIR/$VARIANT-$BENCH-unencoded-mpu-stats.dict.py \;
done


# UNENCODED, NOMPU
if [ $MPUONLY == 0 ]; then
mkdir $BUILD_DIR/x86-unencoded-nompu
cd $BUILD_DIR/x86-unencoded-nompu

$SOURCE_DIR/new_build_env.py -a i386 --encoded no --mpu no

for BENCH in $BENCHMARKS
do
make fail-$BENCH-regs-unencoded-nompu
make fail-$BENCH-mem-unencoded-nompu
make fail-$BENCH-ip-unencoded-nompu

objdump -wC -t -j .data -j .text fail-$BENCH/fail-$BENCH > $START_DIR/$VARIANT-$BENCH-unencoded-nompu.syms
cp fail-$BENCH/fail-$BENCH $START_DIR/$VARIANT-$BENCH-unencoded-nompu.elf
find . -iname stats.dict.py -exec cp '{}' $START_DIR/$VARIANT-$BENCH-unencoded-nompu-stats.dict.py \;
done
fi


# run R evaluation script
cd $START_DIR
Rscript $START_DIR/fail.R $VARIANT $BENCHMARKS

