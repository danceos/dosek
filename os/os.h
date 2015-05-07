#ifndef _DOSEK_OS_OS_H_
#define _DOSEK_OS_OS_H_

#include "os/util/inline.h"
#include "os/helper.h"
#include "os/hooks.h"


EXTERN_C_DECL void os_main(void);
EXTERN_C_DECL void StartOS(int);



/******************************************************************************
 *                                                                            *
 * Macro Definitions                                                          *
 *                                                                            *
 ******************************************************************************/
#define dosek_unused __attribute__((unused))

#define ISR2(taskname) \
	__attribute__((always_inline)) __attribute__((used)) \
    EXTERN_C_DECL void OSEKOS_ISR_##taskname(void)

#define DeclareTask(x)				\
	extern const TaskType OSEKOS_TASK_ ## x;		\
    static dosek_unused const TaskType &x = OSEKOS_TASK_ ## x;	\

/**
 * @satisfies{13,2,5}
 */
#define TASK(taskname) \
	noinline EXTERN_C_DECL void OSEKOS_TASK_FUNC_##taskname(void)

#define ActivateTask(x)				\
  OSEKOS_ActivateTask(OSEKOS_TASK_##x)

#define ChainTask(x)				\
	OSEKOS_ChainTask(OSEKOS_TASK_##x)

#define TerminateTask()				\
  OSEKOS_TerminateTask()

#define Schedule()				\
  OSEKOS_Schedule()

#define DeclareResource(x)				\
	extern const ResourceType OSEKOS_RESOURCE_ ## x;		\
    static dosek_unused const ResourceType &x = OSEKOS_RESOURCE_ ## x;

#define GetResource(x)					\
  OSEKOS_GetResource(OSEKOS_RESOURCE_##x)

#define GetTaskID(x)					\
  OSEKOS_GetTaskID(x)

#define ReleaseResource(x)				\
  OSEKOS_ReleaseResource(OSEKOS_RESOURCE_##x)

#define DeclareEvent(x)							\
	extern const EventMaskType OSEKOS_EVENT_ ## x;			\
    static dosek_unused const EventMaskType &x = OSEKOS_EVENT_ ## x

#define SetEvent(task,event)						\
  OSEKOS_SetEvent(OSEKOS_TASK_##task,event)

#define GetEvent(task,event)						\
  OSEKOS_GetEvent(OSEKOS_TASK_##task,event)

#define ClearEvent(event)				\
  OSEKOS_ClearEvent(event)

#define WaitEvent(event)				\
  OSEKOS_WaitEvent(event)

#define DeclareAlarm(x)				\
	extern const AlarmType OSEKOS_ALARM_ ## x;		\
    static dosek_unused const AlarmType &x = OSEKOS_ALARM_ ## x;

#define ALARMCALLBACK(x)				\
  EXTERN_C_DECL void OSEKOS_ALARMCB_##x()

#define GetAlarm(x,tick)				\
  OSEKOS_GetAlarm(OSEKOS_ALARM_##x,tick)

#define SetRelAlarm(x,inc,period)				\
  OSEKOS_SetRelAlarm(OSEKOS_ALARM_##x,inc,period)

#define SetAbsAlarm(x,inc,period)				\
  OSEKOS_SetRelAlarm(OSEKOS_ALARM_##x,inc,period)

#define CancelAlarm(x)						\
  OSEKOS_CancelAlarm(OSEKOS_ALARM_##x)

#define GetAlarmBase(x,b)				\
  OSEKOS_GetAlarmBase(OSEKOS_ALARM_##x,b)

#define DeclareCounter(x)			\
	extern const CounterType OSEKOS_COUNTER_ ## x;		\
    static dosek_unused const CounterType &x = OSEKOS_COUNTER_ ## x;

#define AdvanceCounter(x)			\
  OSEKOS_AdvanceCounter(OSEKOS_COUNTER_##x)

#define IncrementCounter(x)			\
  OSEKOS_AdvanceCounter(OSEKOS_COUNTER_##x)

#define GetCounter(x)								\
	OSEKOS_GetCounter(OSEKOS_COUNTER_##x)

// #define DeclareMessage(x)						\
// struct MESSAGEStruct OSEKOS_MESSAGE_##x

// #define SendMessage(MSG,DATA)				\
//   OSEKOS_SendMessage(OSEKOS_MESSAGE_##MSG,DATA)
//
// #define ReceiveMessage(MSG,DATA)				\
//   OSEKOS_ReceiveMessage(OSEKOS_MESSAGE_##MSG,DATA)
//
// #define SendDynamicMessage(MSG,DATA,LENGTH)				\
//   OSEKOS_SendDynamicMessage(OSEKOS_MESSAGE_##MSG,DATA,LENGTH)
//
// #define ReceiveDynamicMessage(MSG,DATA,LENGTH)				\
//   OSEKOS_ReceiveDynamicMessage(OSEKOS_MESSAGE_##MSG,DATA,LENGTH)
//
// #define SendZeroMessage(MSG)				\
//   OSEKOS_SendZeroMessage(OSEKOS_MESSAGE_##MSG)

#define ShutdownOS(STATUS)			\
  OSEKOS_ShutdownOS(STATUS)

#define DisableAllInterrupts()                  \
  OSEKOS_DisableAllInterrupts()
#define EnableAllInterrupts()                  \
  OSEKOS_EnableAllInterrupts()
#define SuspendAllInterrupts()                  \
  OSEKOS_SuspendAllInterrupts()
#define ResumeAllInterrupts()                   \
  OSEKOS_ResumeAllInterrupts()
#define SuspendOSInterrupts()                  \
  OSEKOS_SuspendOSInterrupts()
#define ResumeOSInterrupts()                   \
  OSEKOS_ResumeOSInterrupts()



/******************************************************************************
 *                                                                            *
 * API Definitions                                                            *
 *                                                                            *
 ******************************************************************************/

#ifdef __cplusplus
extern "C" {
#endif

/**
 * \brief Artificial function at beginning of a subtask handler
 **/

void OSEKOS_kickoff();


/**
 * \brief Activate a TASK
 * \param t The TASK to be activated
 **/
extern StatusType OSEKOS_ActivateTask(TaskType t);

/**
 * \brief Terminate the calling TASK and immediately activate another TASK
 * \param t The TASK to be activated
 **/
extern __attribute__((noreturn)) StatusType OSEKOS_ChainTask(TaskType t);

/**
 * \brief Terminate the current TASK
 **/
extern __attribute__((noreturn)) StatusType OSEKOS_TerminateTask();

extern StatusType OSEKOS_Schedule();

/**
 * Get current Task's ID
 */
extern StatusType OSEKOS_GetTaskID(TaskRefType a);

/**
 * \brief Acquire a RESOURCE
 * \param r The RESOURCE to be locked
 **/
extern StatusType OSEKOS_GetResource(ResourceType r);

/**
 * \brief Release the given RESOURCE again
 * \param r The RESOURCE to be released
 **/
extern StatusType OSEKOS_ReleaseResource(ResourceType r);

/**
 * \brief Set an EVENT
 * \param t The TASK owning the EVENT
 * \param e The EVENT the will be set
 **/
extern StatusType OSEKOS_SetEvent(TaskType t,EventMaskType e);

/**
 * \brief Get the event mask of the given TASK
 * \param t The TASK owning the EVENT
 * \param e The EVENT the will be set
 **/
extern StatusType OSEKOS_GetEvent(TaskType t, EventMaskRefType e);

/**
 * \brief Clear the given EVENT from the TASKs event mask
 * \param e The EVENT to be cleared
 **/
extern StatusType OSEKOS_ClearEvent(EventMaskType e);

/**
 * \brief Wait for the given event
 **/
extern StatusType OSEKOS_WaitEvent(EventMaskType e);

/**
 * \brief Get the ticks until the next expiration
 **/
extern StatusType OSEKOS_GetAlarm(AlarmType a,TickType* ticks);

/**
 * \brief Trigger the given Alarm to expire in certain amount of time
 * \param a The ALARM to be triggered
 * \param inc The relative offset for the first expiration of the given ALARM
 * \param cycle The ALARM will periodically expire every cycle time units
 **/
extern StatusType OSEKOS_SetRelAlarm(AlarmType a,TickType inc, TickType cycle);

/**
 * \brief Reset the given ALARM
 **/
extern StatusType OSEKOS_CancelAlarm(AlarmType a);

/**
 * \brief Get the AlarmBase
 **/
extern StatusType OSEKOS_GetAlarmBase(AlarmType a,AlarmBaseRefType ab);

/**
 * \brief Advance the given UserCounter c by one tick
 **/
extern StatusType OSEKOS_AdvanceCounter(CounterType c);

/**
 * \brief Send the given Message
 * \param m The MESSAGE to be sent.
 * \param data The content of the message
 **/
extern StatusType OSEKOS_SendMessage(MessageIdentifier m,void *data);

/**
 * \brief Receive the given Message
 * \param m The MESSAGE to be received.
 * \param data The content of the message is stored here.
 **/
extern StatusType OSEKOS_ReceiveMessage(MessageIdentifier m,void *data);

/**
 * \brief Send the given Message of statical unknown lenght
 * \param m The MESSAGE to be sent.
 * \param data The content of the message
 * \param length The lenght of the content in bytes
 **/
extern StatusType OSEKOS_SendDynamicMessage(MessageIdentifier m,void *data,unsigned int length);

/**
 * \brief Receive the given Message
 * \param m The MESSAGE to be received.
 * \param data The content of the message is stored here
 * \param length The lenght of the content in bytes
 **/
extern StatusType OSEKOS_ReceiveDynamicMessage(MessageIdentifier m,void *data,unsigned int length);

/**
 * \brief Send a message without content
 **/
extern StatusType OSEKOS_SendZeroMessage(MessageIdentifier m);

/**
 * \brief Methods for interrupt disabling/enabling. This pair cannot
 *        be stacked.
 **/
extern void OSEKOS_DisableAllInterrupts();
extern void OSEKOS_EnableAllInterrupts();

/**
 * \brief Same as disable/enable but can be stacked.
 **/
extern void OSEKOS_SuspendAllInterrupts();
extern void OSEKOS_ResumeAllInterrupts();
extern void OSEKOS_SuspendOSInterrupts();
extern void OSEKOS_ResumeOSInterrupts();

/******************************************************************************
 *                                                                            *
 * API Definitions (not supported, not creating any dependencies              *
 *                                                                            *
 ******************************************************************************/

extern __attribute__((noreturn)) void OSEKOS_ShutdownOS(StatusType status);


#ifdef __cplusplus
}
#endif

#endif
