## Add *additional* architecture specific compiler flags here.
# Note that the flags set in toolchain.cmake are still present and used.

set(ISA_C_FLAGS "" PARENT_SCOPE)
set(ISA_CXX_FLAGS "" PARENT_SCOPE)
set(ISA_ASM_FLAGS "-m32" PARENT_SCOPE)
set(ISA_LD_FLAGS "" PARENT_SCOPE)


set(LD_OUTPUT_FORMAT "elf32-i386" CACHE INTERNAL "LD output format for linker script")

## The kernel will live at 3GB + 1MB in the virtual
##   address space, which will be mapped to 1MB in the
##   physical address space.
set(LD_KERNEL_START_ADDRESS 0x100000 CACHE INTERNAL "Start address of the first section.")

