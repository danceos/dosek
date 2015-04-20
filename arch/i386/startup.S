## Bare bone boot.s from wiki.osdev.org

# multiboot header
.section .rodata.multiboot
.align 4

# magic number
.long 0x1BADB002

# flags: align, meminfo
.long 0x3

# checksum: -(magic+flags)
.long -(0x1BADB002 + 0x3)



# the initial kernel stack
.section .kernel_stack
.global os_stack
.size os_stack, 4096
#.Lstack_bottom:
os_stack:
.byte 0
#.skip 16384 # 16 KiB
.skip 4094 # 4 KiB
.byte 0
.Lstack_top:



# The linker script specifies _start as the entry point to the kernel and the
# bootloader will jump to this position once the kernel has been loaded. It
# doesn't make sense to return from this function as the bootloader is gone.
.section .text.startup
.global _start
.type _start, @function
_start:
	# Welcome to kernel mode! 
	# To set up a stack, we simply set the esp register to point to the top of
	# our stack (as it grows downwards).
	movl $.Lstack_top, %esp
	# We are now ready to actually execute C code. (see ./startup.cc)
	call arch_startup

	# In case the function returns, we'll want to put the computer into an
	# infinite loop. To do that, we use the clear interrupt ('cli') instruction
	# to disable interrupts, the halt instruction ('hlt') to stop the CPU until
	# the next interrupt arrives, and jumping to the halt instruction if it ever
	# continues execution, just to be safe. We will create a local label rather
	# than real symbol and jump to there endlessly.
	cli
	hlt
.Lhang:
	jmp .Lhang

# Set the size of the _start symbol to the current location '.' minus its start.
# This is useful when debugging or when you implement call tracing.
.size _start, . - _start
