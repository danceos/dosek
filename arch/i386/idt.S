#define IRQS_BASE 0x101000
#define IRQS_OFFSET 32
#define KERNEL_CODE_SEGMENT 0x8
#define TYPE_DPL0_IRQ_GATE  0x8E
#define TYPE_DPL0_TRAP_GATE 0x8F
#define TYPE_DPL3_IRQ_GATE  0xEE


# IRQ handler macro
#
# num: IRQ number
# error_code: 1 if this IRQ pushes an error code to the stack
# type: IDT gate type
.macro  IRQ num, error_code=0, type=TYPE_DPL0_IRQ_GATE

# define new handler in irqhandlers section
.section .text.irqhandlers
# align on IRQS_OFFSET bytes to calculate static offsets
.align IRQS_OFFSET

# IRQ entry point
irq_\num:
	jmp irq_handler_\num

# actual IRQ handler
#
# this is a weak symbol to allow overriding the default handler
# the entry point above cannot be a weak symbol as it needs a static
# address for the IDT
.weak irq_handler_\num
.type irq_handler_\num, @function
irq_handler_\num:
	# x86 ABI mandates direction flag
	cld

	# push dummy error code if necessary
	.if !\error_code
	push $0
	.endif

	# push general purpose registers
	pusha

	# save stack pointer
	mov %esp, %esi

	# switch to kernel stack
	# TODO: where to start interrupt stack?
	mov $_estack_os-2048, %esp

	# save IRQ number in register (for default ISR)
	mov $\num, %eax

	# jump to ISR
	jmp isr_\num


# the default ISR
.section .text.isrs
.weak isr_\num
isr_\num:
	# jump to default handler
	jmp unhandled_handler


# add IDT entry to idt section
.section .text.idt
	.short ((IRQS_BASE + \num*IRQS_OFFSET) & 0xFFFF)
	.short KERNEL_CODE_SEGMENT
	.byte 0
	.byte \type
	.short (IRQS_BASE + \num*IRQS_OFFSET) >> 16
.endm



# put IDT in separate section
.section .text.idt
.global theidt
theidt:
	# filled by IRQ macro



# the IRQ handlers
.section .text.irqhandlers
.global irq_handlers
irq_handlers:
# CPU exceptions
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
IRQ 15
IRQ 16
IRQ 17, 1
.irp irqno, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
IRQ \irqno
.endr

# PIC interrupts
.irp irqno, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47
IRQ \irqno
.endr

# OS interrupts (DPL3 to allow calling from ring 3)
.irp irqno, 48, 49, 50
IRQ \irqno, 0, TYPE_DPL3_IRQ_GATE
.endr

# other interrupts
.irp irqno, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255
IRQ \irqno
.endr



# common IRQ exit code
.global handler_exit
handler_exit:
	# switch back to original stack
	mov %esi, %esp

	# pop general purpose registers
	popa

	# restore original stack pointer
	add $0x4, %esp

	# return from interrupt
	iret