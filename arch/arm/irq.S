# start address of interrupt handlers
#define IRQS_BASE 0x101000

# offset between irq handler addresses
#define IRQS_OFFSET 256

.syntax unified

.section .text.irq_vectors
.align 4

.arm
.global interrupt_vector_table
interrupt_vector_table:
    b _boot		@ Reset
    b panic_a			@ Undefined instruction
    b syscall_hndlr	@ SWI instruction
    b panic_b			@ Prefetch Abort
    b panic_c			@ Data Abort
    b panic_d			@ reserved
    b irq_entry		@ IRQ
    b firq_hndlr	@ FIRQ

.section .text.irq_handlers

panic_a:
    mov r0, 0xaa
    b panic

panic_b:
    mov r0, 0xbb
    b panic

panic_c:
    mov r0, 0xcc
    b panic

panic_d:
    mov r0, 0xdd
    b panic

.global panic
panic:
	# bkpt

	ldr sp, =_estack_os-16
	sub lr, lr, #4
	push {lr}
	push {r0,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12}
	mov r0, sp
	blx kernel_dump
	b .
.size panic, . - panic

.extern __OS_HOOK_FaultDetectedHook

.global irq_entry
irq_entry:
    # Switch to the OS stack
	ldr sp, =_estack_os
    # Calculate the return address
    sub lr, lr, #4
    # Store LR and SPSR to the task's stack (adjust task's SP)
    srsdb sp, #31
    # Store the user's SP on our stack. we need do do this dance,
    # since ! does not work with this special version of stm
    stmdb sp, {sp}^
    nop
    sub sp, sp, #4
    # Load the User Stack pointer into LR
    ldmia sp!, {lr}
    # Virtually do the increment, the SRSDB has not written back
    sub lr, lr, #8
    # Push the task's registers to the user stack
    stmdb lr, {r0-lr}^
    sub   lr, lr, #60
#ifdef CONFIG_DEPENDABILITY_ENCODED
	# XOR task context checksum
	eor r1, r0,  r1
	eor r1, r2,  r1
	eor r1, r3,  r1
	eor r1, r4,  r1
	eor r1, r5,  r1
	eor r1, r6,  r1
	eor r1, r7,  r1
	eor r1, r8,  r1
	eor r1, r9,  r1
	eor r1, r10, r1
	eor r1, r11, r1
	eor r1, r12, r1
    # load stored CPSR:
	ldr r0, [lr,#64]
	eor r1, r0, r1
    # load stored user return:
	ldr r0, [lr,#60]
	eor r1, r0, r1
	# load stored user lr:
    ldr r0, [lr,#56]
	eor r1, r0, r1
    # load stored user sp:
	ldr r0, [lr,#52]
	eor r1, r0, r1
	# Store checksum on stack
	stmdb lr!, {r1}
#endif
    #--------- User's registers are safe ------
	# Task's SP is 1st argument
	mov r0, lr
    # Save our return point to the user stack
    adr r1, irq_entry_return
    stmdb lr!, {r1}
#ifdef CONFIG_DEPENDABILITY_ENCODED
    # Push the return address twice
    stmdb lr, {r1}
#endif
    # Branch with link, and exchange instruction set: ARM to Thumb
	blx irq_handler
.global irq_entry_return
irq_entry_return:
    # This NOP is important!
    nop
    # r0 is the stack pointer we want to return to
    mov lr, r0

#ifdef CONFIG_DEPENDABILITY_ENCODED
	# ignore stored checksum
	add lr, lr, #4
	# load store registers
	ldmia lr, {r0-r12,sp,lr}^
	# Get checksum from stack
	ldr r1, [lr,-4]
	eor r1, r0,  r1
	eor r1, r2,  r1
	eor r1, r3,  r1
	eor r1, r4,  r1
	eor r1, r5,  r1
	eor r1, r6,  r1
	eor r1, r7,  r1
	eor r1, r8,  r1
	eor r1, r9,  r1
	eor r1, r10, r1
	eor r1, r11, r1
	eor r1, r12, r1
	# also check stored sp:
	ldr r0, [lr,#52]
	eor r1, r0, r1
	# and stored lr:
	ldr r0, [lr,#56]
	eor r1, r0, r1
    # load stored user return:
	ldr r0, [lr,#60]
	eor r1, r0, r1
    # load stored CPSR:
	ldr r0, [lr,#64]
	eor r1, r0, r1
	# r1 should now equal the original r1 stored on stack (lr+4)
	# let's check this:
	ldr r2, [lr,4]
	teq r2, r1
	beq 1f
	# Set fault detected type (1==XORdetected)
	mov r0, 1
	# save lr (= stack pointer) in callee saved register
	mov r4, lr
	blx __OS_HOOK_FaultDetectedHook
    # fix lr
	mov lr, r4
1:
    # restore r0 - r4
	ldmia lr, {r0-r4}
#else
    # Pop the register set
    ldmia lr, {r0-r12,sp,lr}^
#endif
    # Pop the register set
	add   lr, lr, #60
    rfeia lr
    nop
.size irq_entry, . - irq_entry


.global firq_hndlr
firq_hndlr:
	# mov sp, %[ps] : : [ps]"i" (KSTACKEXC));
	# sub lr, lr, #4
	# push {lr}
	# push {r0,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12}
	# mov %[ps], lr : [ps]"=r" (lr)

	bkpt

	#b handler_exit
.size firq_hndlr, . - firq_hndlr


.global syscall_hndlr
syscall_hndlr:
   ldr sp, =_estack_os-16
   blx syscall_handler
.size syscall_hndlr, . - syscall_hndlr

