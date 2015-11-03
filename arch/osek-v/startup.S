
.section .text.vectors
mentry_user_mode:
    # This will be placed at 0x100
    # from user mode
    li a0, 0x00
    j bad_trap
.size mentry_user_mode, . - mentry_user_mode

.align  6;
mentry_supervisor_mode:
    # from supervisor mode (mtvec + 0x40)
    li a0, 0x40
	jal bad_trap
.size mentry_supervisor_mode, . - mentry_supervisor_mode


.align 6
mentry_hypervisor_mode:
    # from hypervisor mode (mtvec + 0x80)
	li a0, 0x80
	jal bad_trap
.size mentry_hypervisor_mode, . - mentry_hypervisor_mode


# from machine mode (mtvec + 0xc0)
.global mentry_machine_mode
.align 6
mentry_machine_mode:
    csrw mscratch, sp
    addi sp, sp, -32*8
    j interrupt_handler_asm
.size mentry_machine_mode, . - mentry_machine_mode


.section .text.boot
.align  8;
.global _start;
_start:
    lla sp, os_stack
    add sp, sp, 1024-16
    jal arch_startup
.size _start, . - _start

.global idle_entry
idle_entry:
    lla sp, os_stack
    add sp, sp, 1024-16
    jal __OS_HOOK_PreIdleHook
1:
    wfi
    j 1b
.size idle_entry, . - idle_entry

.global interrupt_handler
.global interupt_handler_asm
interrupt_handler_asm:
	sd ra, 1*8(sp)
    sd a0, 10*8(sp)
    sd a1, 11*8(sp)

    # Store the user stackpointer
	csrrw a1, mscratch, sp           # ra <- user sp
	sd a1, 2*8(sp)            # sp
    csrr a0, mcause

    sd gp, 3*8(sp)
	sd tp, 4*8(sp)
	sd t0, 5*8(sp)
	sd t1, 6*8(sp)
	sd t2, 7*8(sp)
	sd s0, 8*8(sp)
	sd s1, 9*8(sp)
	sd a2, 12*8(sp)
	sd a3, 13*8(sp)
	sd a4, 14*8(sp)
	sd a5, 15*8(sp)
	sd a6, 16*8(sp)
	sd a7, 17*8(sp)
	sd s2, 18*8(sp)
	sd s3, 19*8(sp)
	sd s4, 20*8(sp)
	sd s5, 21*8(sp)
	sd s6, 22*8(sp)
	sd s7, 23*8(sp)
	sd s8, 24*8(sp)
	sd s9, 25*8(sp)
	sd s10, 26*8(sp)
	sd s11, 27*8(sp)
	sd t3,  28*8(sp)
	sd t4,  29*8(sp)
	sd t5,  30*8(sp)
	sd t6,  31*8(sp)

    jal interrupt_handler

	ld ra, 1*8(sp)
    # sp is restored at end
	ld gp, 3*8(sp)
	ld tp, 4*8(sp)
	ld t0, 5*8(sp)
	ld t1, 6*8(sp)
	ld t2, 7*8(sp)
	ld s0, 8*8(sp)
	ld s1, 9*8(sp)
	ld a0, 10*8(sp)
	ld a1, 11*8(sp)
	ld a2, 12*8(sp)
	ld a3, 13*8(sp)
	ld a4, 14*8(sp)
	ld a5, 15*8(sp)
	ld a6, 16*8(sp)
	ld a7, 17*8(sp)
	ld s2, 18*8(sp)
	ld s3, 19*8(sp)
	ld s4, 20*8(sp)
	ld s5, 21*8(sp)
	ld s6, 22*8(sp)
	ld s7, 23*8(sp)
	ld s8, 24*8(sp)
	ld s9, 25*8(sp)
	ld s10, 26*8(sp)
	ld s11, 27*8(sp)
	ld t3,  28*8(sp)
	ld t4,  29*8(sp)
	ld t5,  30*8(sp)
	ld t6,  31*8(sp)

    ld sp, 2*8(sp)
    eret

.size interrupt_handler_asm, . - interrupt_handler_asm

.global __switch_to
__switch_to:
	/* Save context into prev->thread */
	sd ra,  0*8(a0)
	sd sp,  1*8(a0)
	sd s0,  2*8(a0)
	sd s1,  3*8(a0)
	sd s2,  4*8(a0)
	sd s3,  5*8(a0)
	sd s4,  6*8(a0)
	sd s5,  7*8(a0)
	sd s6,  8*8(a0)
	sd s7,  9*8(a0)
	sd s8,  10*8(a0)
	sd s9,  11*8(a0)
	sd s10, 12*8(a0)
	sd s11, 13*8(a0)
__switch_to__half:
	/* Restore context from next->thread */
	ld ra,  0*8(a1)
	ld sp,  1*8(a1)
	ld s0,  2*8(a1)
	ld s1,  3*8(a1)
	ld s2,  4*8(a1)
	ld s3,  5*8(a1)
	ld s4,  6*8(a1)
	ld s5,  7*8(a1)
	ld s6,  8*8(a1)
	ld s7,  9*8(a1)
	ld s8,  10*8(a1)
	ld s9,  11*8(a1)
	ld s10, 12*8(a1)
	ld s11, 13*8(a1)
	mv tp, a1 /* Next current pointer */
	ret
.size __switch_to, . - __switch_to

.global __start_to
__start_to:
	/* Restore context from next->thread */
	ld ra,  0*8(a0)
	ld sp,  1*8(a0)
	ld s0,  2*8(a0)
	ld s1,  3*8(a0)
	ld s2,  4*8(a0)
	ld s3,  5*8(a0)
	ld s4,  6*8(a0)
	ld s5,  7*8(a0)
	ld s6,  8*8(a0)
	ld s7,  9*8(a0)
	ld s8,  10*8(a0)
	ld s9,  11*8(a0)
	ld s10, 12*8(a0)
	ld s11, 13*8(a0)
	mv tp, a1 /* Next current pointer */
	ret
.size __start_to, . - __start_to
