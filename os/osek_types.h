#ifndef __dosek_osek_types
#define __dosek_osek_types

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
	E_OK = 0,
	E_OS_ACCESS = 1,
	E_OS_CALLEVEL = 2,
	E_OS_ID = 3,
	E_OS_LIMIT = 4,
	E_OS_NOFUNC = 5,
	E_OS_RESOURCE = 6,
	E_OS_STATE = 7,
	E_OS_VALUE = 8,
	E_NOT_OK = 9,
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

/******************************************************************************
 *                                                                            *
 * Data Type Definitions                                                      *
 *                                                                            *
 ******************************************************************************/

typedef uint32_t TaskType;
typedef uint32_t* TaskRefType;

typedef uint32_t ResourceType;

typedef unsigned long EventMaskType;

typedef uint32_t AlarmType;

typedef struct {
	unsigned long maxallowedvalue;
	unsigned long ticksperbase;
	unsigned long mincycle;
} AlarmBaseType;

typedef AlarmBaseType* AlarmBaseRefType;

typedef uint32_t CounterType;

typedef uint32_t MessageIdentifier;

typedef uint16_t TickType;
typedef TickType * TickRefType;



#endif
