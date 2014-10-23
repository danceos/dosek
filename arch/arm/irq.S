# start address of interrupt handlers
#define IRQS_BASE 0x101000

# offset between irq handler addresses
#define IRQS_OFFSET 256

.syntax unified

.section .text.irq_vectors
.align 4

.arm
interrupt_vector_table:
    b _start		@ Reset
    b panic			@ Undefined instruction
    b syscall_hndlr	@ SWI instruction
    b panic			@ Prefetch Abort
    b panic			@ Data Abort
    b panic			@ reserved
    b irq_entry		@ IRQ
    b firq_hndlr	@ FIRQ


.section .text.irq_handlers

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
    stmdb lr, {r0-r12,sp,lr}^
    sub   lr, lr, #60
    #--------- User's registers are safe ------
	# Task's SP is 1st argument
	mov r0, lr
    # Save our return point to the user stack
    adr r1, irq_entry_return
    stmdb lr!, {r1}
    # Branch with link, and exchange instruction set: ARM to Thumb
	blx irq_handler
irq_entry_return:
    # This NOP is important!
    nop
    # r0 is the stack pointer we want to return to
    mov lr, r0
    # Remove return address (1:) from user stack
    # ldmia lr!, {r0}
    # Pop the register set
    ldmia lr, {r0-r12,sp,lr}^
    add   sp, lr, #60
    rfeia sp!
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

