
.global mp_setup
.global mp_setup_end

mp_setup:
.code16
	# Set segments
	movw %cs,%ax
	movw %ax,%ds
	movw %ax,%es
	movw %ax,%fs
	movw %ax,%ss

	# Disable interrupts
	cli
	# Disable non-maskable interrupts
	movb $0x80,%al
	outb %al,$0x70

	# Load interrupt descriptor table
	lidtw ap_idt_entry - mp_setup
	# Load global descriptor table
	lgdtw ap_gdt_entry - mp_setup

	# Enable protected mode
	movl %cr0,%eax
	or   $1,%eax
	movl %eax,%cr0

	# Far jump to _mp_start setting the cs register to 0x08
	ljmpl $0x08,$_mp_start

	hlt

ap_gdt:
	.word 0,0,0,0	# NULL Deskriptor

	.word 0xffff	# 4GB
	.word 0x0000	# Base address 0
	.word 0x9a00	# code read/exec
	.word 0x00cf	# granularity = 4096, 386 (and limit)

	.word 0xffff	# 4GB
	.word 0x0000	# Base address 0
	.word 0x9200	# read/write
	.word 0x00cf	# granularity = 4096, 386 (and limit)

ap_gdt_entry:
	.word 0x18								# 24 Bytes = 3 entries
	.long 0x40000 + ap_gdt - mp_setup		# physical address of gdt

ap_idt_entry:
	.word 0			# Limit
	.word 0,0		# Base

mp_setup_end:
	nop
