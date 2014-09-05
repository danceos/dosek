.syntax unified

.align 4

.section .text.startup
.global _start
.type _start, function
.arm
_start:
	# setup startup stack
	ldr sp, =_estack_os-16

	# debug loop
	mov r0, #42
loop:
	cmp r0, #0
	#bne loop

	# continue to C startup code in startup.cc
	blx arch_startup

	# should never come here
	bkpt

.size _start, . - _start
