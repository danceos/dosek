CoRedOS - Combined Redundancy Operating System
----------------------------------------------

Requirements:
 * Clang >= 3.3
 * LLVM >= 3.3
 * cmake
 * python
 `- llvmpy
 * grub-mkrescue for bulding bootable x86 isosA
 * qemu-system-i386 for testing x86
 * (doxygen)

Build instructions:
 - Make a build directory: mkdir build
 - Prepare build environment: cd build && ../new_build_env.py
 - Show available build targets: make help
 - Show short target description: make h
 - Build and run all test cases: make build_and_test

after_first_checkout.sh is only necessary, if you are going to contribute
via our gerrit code review system.
