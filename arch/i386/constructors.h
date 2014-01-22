#ifndef _UTIL_CONSTRUCTORS_H
#define _UTIL_CONSTRUCTORS_H
/**
 *  @ingroup arch
 *  @defgroup generic Generic architecture functionalities
 *  @brief Generic hardware near implementations.
 *
 *  This includes, for example, the execution of global constructors.
 */

/**
 * @file 
 * @ingroup generic
 * @brief Run global constructors at system startup.
 */

extern "C" {
  /**
   * @brief To be execute at startup.
   */
	void run_constructors();
}
#endif
