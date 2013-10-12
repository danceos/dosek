#ifndef __MACHINE_H__
#define __MACHINE_H__
/**
 *  @ingroup arch
 *  @defgroup i386 i386 Hardware
 *  @brief Architecture specific code for the i386 hardware.
 */

/**
 * @file
 *
 * @ingroup i386
 *
 * @brief Machine dependent special instructions.
 */

/**
 * \brief Machine dependent special instructions.
 * This struct provides static inline methods implementings some machine 
 * specific instructions.
 */
struct Machine
{
  /**
   * \brief Emits a nop opcode. (nop)
   */
  static void nop(void) {
    __asm__ volatile ("nop");
  };

  /**
   * \brief Halts the machine. (hlt)
   */
  static void halt(void) {
    __asm__ volatile ("hlt");
  }

  /**
   * \brief Emits an undefined instruction trap.
   * Used for runtime asserts.
   */
  static void debug_trap(void) {
    __asm__ volatile ("ud2");
  }
};

#endif // __MACHINE_H__
