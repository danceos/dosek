# start address of interrupt handlers
#define IRQS_BASE 0x101000

# offset between irq handler addresses
#define IRQS_OFFSET 128

# kernel code GDT segment
#define KERNEL_CODE_SEGMENT 0x8

# handler gate types
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
.align IRQS_OFFSET, 0xcc

# IRQ entry point
.global irq_\num
irq_\num:
	jmp irq_handler_\num

.size irq_\num, . - irq_\num

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
	pushl $0
	.endif

	# jump to label 1 if coming from user task (check page directory)
	push %eax # save eax on stack to reuse it
	mov %cr3, %eax # get page directory
	.weak pagedir_os
	cmp $pagedir_os,%eax # if kernel page directory we are not from task
	jne 1f

	# coming from kernel: save context on interrupt stack
	pop %eax # restore eax
	pusha # save all registers
	leal 32(%esp), %esi # put interrupt stack pointer in %esi
	mov %esp, %ebx # put context pointer in %ebx
	jmp 2f # jump over user mode handling

1:
	# coming from task: save context on userspace/task stack
	mov %esp, %eax # save interrupt stackpointer in eax
	mov 20(%esp), %esp # switch (back) to userspace stack
	push 8(%eax) # save return address on stack
	push 16(%eax) # save flags on stack
	pusha # save all registers
	mov %esp, %ebx # put context pointer in %ebx
	push $irq_resume # push irq_resume fragment as "new" return address
	mov (_ZN4arch7save_spE), %ecx # get value of arch::save_sp
	mov %ebx, (%ecx) # save stack pointer to *arch::save_sp
	mov %eax, %esp # switch back to interrupt stack
	pop %eax # restore eax
	mov %eax, 28(%ebx) # put real userspace eax in saved context
	mov %esp, %esi # put interrupt stack pointer in %esi

2:
	# save IRQ number in register (for isr_unhandled)
	mov $\num, %eax

	# jump to ISR
	jmp isr_\num

.size irq_handler_\num, . - irq_handler_\num



# the default ISR
# also a weak symbol to allow overriding
.section .text.isrs
.weak isr_\num
isr_\num:
	# jump to default handler
	jmp isr_unhandled

.size isr_\num, . - isr_\num



# add IDT entry to idt section
.section .text.idt
	.short ((IRQS_BASE + \num*IRQS_OFFSET) & 0xFFFF) # handler address
	.short KERNEL_CODE_SEGMENT # handler code segment
	.byte 0 # always zero
	.byte \type # gate type
	.short (IRQS_BASE + \num*IRQS_OFFSET) >> 16 # handler address
.size theidt, . - theidt

.endm # end of IRQ macro



# separate section for IDT
.section .text.idt
.global theidt
.type theidt, @object
theidt:
	# filled by IRQ macro



# the IRQ handlers
.section .text.irqhandlers
.global irq_handlers
irq_handlers:
# CPU exceptions
# TODO: use trap gate if possible?
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

# OS interrupts (DPL3 to allow calling from ring 3)
.irp irqno, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47
IRQ \irqno, 0, TYPE_DPL3_IRQ_GATE
.endr

# other interrupts
.irp irqno, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255
IRQ \irqno
.endr

.section .text.irqhandlers
.size irq_handlers, . - irq_handlers

.section .text.idt
.size theidt, . - theidt


.section .text.irqhandlers

# common IRQ exit code
.global handler_exit
.type handler_exit, @function
handler_exit:
	# restore interrupt stack pointer from %esi
	mov %esi, %esp

	# pop general purpose registers from %ebx
	mov (%ebx), %edi
	mov 4(%ebx), %esi
	mov 8(%ebx), %ebp
	mov 20(%ebx), %edx
	mov 24(%ebx), %ecx
	mov 28(%ebx), %eax
	mov 16(%ebx), %ebx

	# restore original stack pointer
	add $0x4, %esp

	# return from interrupt
	iret

.size handler_exit, . - handler_exit



# common task resumption code
.global irq_resume
.type irq_resume, @function
irq_resume:
	# restore and remove saved context
	popa

	# restore saved flags
	popf

	# remove and jump back to saved instruction pointer
	ret

.size irq_resume, . - irq_resume