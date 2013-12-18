# put irqhandlers in separate section
.section .text.irqhandlers

# IRQ handler macro
#   num: IRQ number
#   error_code: 1 if this IRQ pushes an error code to the stack
.macro  IRQ num, error_code=0

# align on 16 bytes to calculate static offsets
.align 16
.global handler\num
.type handler\num, @function

handler\num:
	# push dummy code if IRQ without error code
	.if !\error_code
	push $0
	.endif

	# push IRQ number
	# TODO: replace this error-prone value by "unrolled" handlers
	push $\num

	# jump to common IRQ handler code
	jmp handler_common

.endm

# the IRQ handlers
.global irq_handlers
irq_handlers:
IRQ 0
IRQ 1
IRQ 2
IRQ 3
IRQ 4
IRQ 5
IRQ 6
IRQ 7
IRQ 8, 1
IRQ 9
IRQ 10, 1
IRQ 11, 1
IRQ 12, 1
IRQ 13, 1
IRQ 14, 1
IRQ 16
IRQ 17, 1
IRQ 18
IRQ 19
IRQ 20
IRQ 30
IRQ 32
IRQ 33



# common IRQ handler code
.global handler_common
handler_common:
	# x86 ABI mandates direction flag
	cld

	# push general purpose registers
	pusha

	# save stack pointer
	mov %esp, %esi

	# switch to kernel stack
	# TODO: where to start interrupt stack?
	mov $_estack_os-2048, %esp

	# *jump* to C handler function
	jmp irq_handler



# common IRQ exit code
.global handler_exit
handler_exit:
	# switch back to user stack
	mov %esi, %esp

	# pop general purpose registers
	popa

	# restore original stack pointer
	add $0x8, %esp

	# return from interrupt
	iret