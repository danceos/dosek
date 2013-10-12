#ifndef __MACHINE_H__
#define __MACHINE_H__

/**
 * \brief Machine dependent special instructions.
 */
struct Machine
{
  /**
   * Nop opcode
   */
  static void nop(void) {
    __asm__ volatile ("nop");
  };

  /**
   * Halt the machine
   */
  static void halt(void) {
    __asm__ volatile ("hlt");
  }

  /*
   * Emit a undefined instruction trap.
   * Used for runtime asserts.
   */
  static void debug_trap(void) {
    __asm__ volatile ("ud2");
  }
};

#endif // __MACHINE_H__
