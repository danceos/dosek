
.global mp_stack
.global _mp_start

mp_stack:
	.long 0

_mp_start:
	# Initialize segment descriptors.
	# The GDT that was set up in mp_setup in real mode is used. Therefore
	# the memory that was copied to 0x40000 is expected not to be overwritten.
	movl $0x10,%eax
	movl %eax,%ss
	movl %eax,%ds
	movl %eax,%gs
	movl %eax,%fs
	movl %eax,%es

	# Setup stack
	movl $mp_stack,%esp

	# For gcc compiled code
	cld

	# Enter C++ Code
	jmp mp_startup

	# Loop forever
	cli
.Lhang:
	hlt
	jmp .Lhang

