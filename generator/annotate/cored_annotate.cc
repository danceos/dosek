#include "os.h"
#include "rtsc_annotate.h"
#include "depsvc.h"

extern "C" {

void OSEKOS_kickoff(void) {
	rtsc_systemcall();
}

StatusType OSEKOS_ActivateTask(TaskType t) {
  rtsc_systemcall();
  rtsc_annotate_os_param(t);
}

StatusType OSEKOS_ChainTask(TaskType t)  {
  rtsc_systemcall();
  rtsc_annotate_os_param(t);
}

StatusType OSEKOS_TerminateTask()  {
  rtsc_systemcall();
}

StatusType OSEKOS_Schedule()  {
  rtsc_systemcall();
}

StatusType OSEKOS_GetResource(ResourceType r)  {
  rtsc_systemcall();
  rtsc_annotate_os_param(r);
}

StatusType OSEKOS_ReleaseResource(ResourceType r) {
  rtsc_systemcall();
  rtsc_annotate_os_param(r);
}

StatusType OSEKOS_SetEvent(TaskType t,EventMaskType e) {
  rtsc_systemcall();
  rtsc_annotate_os_param(t);
  rtsc_annotate_os_param((void*)e);
}

StatusType OSEKOS_GetEvent(TaskType t,EventMaskType e) {
  rtsc_systemcall();
  rtsc_annotate_os_param(t);
  rtsc_annotate_os_param((void*)e);
}

StatusType OSEKOS_ClearEvent(EventMaskType e) {
  rtsc_systemcall();
  rtsc_annotate_os_param((void*)e);
}

StatusType OSEKOS_WaitEvent(EventMaskType e) {
  rtsc_systemcall();
  rtsc_annotate_os_param((void*)e);
}

StatusType OSEKOS_GetAlarm(AlarmType a, TickType* ticks) {
  rtsc_systemcall();
  rtsc_annotate_os_param(a);
  rtsc_annotate_app_param((void*)ticks);
}

StatusType OSEKOS_SetRelAlarm(AlarmType a, TickType inc, TickType cycle) {
  rtsc_systemcall();
  rtsc_annotate_os_param(a);
  rtsc_annotate_app_param((void*)inc);
  rtsc_annotate_app_param((void*)cycle);
}

StatusType OSEKOS_SetAbsAlarm(AlarmType a, TickType inc, TickType cycle) {
  rtsc_systemcall();
  rtsc_annotate_os_param(a);
  rtsc_annotate_app_param((void*)inc);
  rtsc_annotate_app_param((void*)cycle);
}

StatusType OSEKOS_CancelAlarm(AlarmType a) {
  rtsc_systemcall();
  rtsc_annotate_os_param(a);
}

StatusType OSEKOS_AdvanceCounter(CounterType c) {
  rtsc_systemcall();
  rtsc_annotate_os_param(c);
}

StatusType OSEKOS_SendMessage(MessageIdentifier m,void *data) {
  rtsc_systemcall();
  rtsc_annotate_os_param(m);
  rtsc_annotate_app_param((void*)data);
}

StatusType OSEKOS_ReceiveMessage(MessageIdentifier m,void *data) {
  rtsc_systemcall();
  rtsc_annotate_os_param(m);
  rtsc_annotate_app_param((void*)data);
}

StatusType OSEKOS_SendDynamicMessage(MessageIdentifier m,void *data,unsigned int length) {
  rtsc_systemcall();
  rtsc_annotate_os_param(m);
  rtsc_annotate_app_param((void*)data);
  rtsc_annotate_app_param((void*)length);
}

StatusType OSEKOS_ReceiveDynamicMessage(MessageIdentifier m,void *data,unsigned int length) {
  rtsc_systemcall();
  rtsc_annotate_os_param(m);
  rtsc_annotate_app_param((void*)data);
  rtsc_annotate_app_param((void*)length);
}

StatusType OSEKOS_SendZeroMessage(MessageIdentifier m) {
  rtsc_systemcall();
  rtsc_annotate_os_param(m);
}


void OSEKOS_ShutdownOS(StatusType m) {
  rtsc_systemcall();
  rtsc_annotate_os_param((void*)m);

}

void OSEKOS_DisableAllInterrupts() {
    rtsc_systemcall();
}
void OSEKOS_EnableAllInterrupts() {
    rtsc_systemcall();
}
void OSEKOS_SuspendAllInterrupts() {
    rtsc_systemcall();
}
void OSEKOS_ResumeAllInterrupts() {
    rtsc_systemcall();
}
void OSEKOS_SuspendOSInterrupts() {
    rtsc_systemcall();
}
void OSEKOS_ResumeOSInterrupts() {
    rtsc_systemcall();
}


void OSEKOS_AcquireCheckedObject(struct CHECKEDOBJECTStruct *) {
	rtsc_systemcall();
}

void OSEKOS_ReleaseCheckedObject(struct CHECKEDOBJECTStruct *) {
	rtsc_systemcall();
}

}
