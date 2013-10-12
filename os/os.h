/**
 *  @defgroup os Operating System Layer
 *  @brief This modules provides all OS functionalities
 */

/**
 * @file
 * @ingroup os
 * @brief OSEK API header
 */

/**
 * @satisfies{13,1}
 */
typedef enum  {
  E_OS_ACCESS = 1,
  E_OS_CALLEVEL = 2,
  E_OS_ID = 3,
  E_OS_LIMIT = 4,
  E_OS_NOFUNC = 5,
  E_OS_RESOURCE = 6,
  E_OS_STATE = 7,
  E_OS_VALUE = 8,
} StatusType;

/**
 * @satisfies{13,2,4}
 */
enum TaskStateType {
  RUNNING = 1,    //!< Constant of data type TaskStateType for task state *running*
  WAITING,        //!< Constant of data type TaskStateType for task state *waiting*
  READY,          //!< Constant of data type TaskStateType for task state *ready*
  SUSPENDED,      //!< Constant of data type TaskStateType for task state *suspended*
  INVALID_TASK,   //!< Constant of data type TaskStateType for a not defined task
};


/**
 * @satisfies{13,2,5}
 * @todo This is just a stub for testing doxygen
 */
#define TASK(taskname) void start_##taskname (void)
