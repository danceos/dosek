#ifndef __rtsc_annotate_h__
#define __rtsc_annotate_h__

#include "os.h"

/******************************************************************************
 *                                                                            *
 * Annotations to describe OSEKOS-Systemcalls                                 *
 *                                                                            *
 ******************************************************************************/

/**
 * This annotation indicates that the caller is part of the OS API
 **/
void rtsc_systemcall();

/**
 * This annotation indicates that a particular parameter is a parameter 
 * belonging to the application, so this parameter must not be eliminated when
 * cleaning up the OS API Calls of the source system.
 *
 * Example:
 * 
 * void setData(Message *m,void *data) {
 *   llvm_annotate_application_param(data);
 * }
 *
 * This indicates that the parameter data carries application related 
 * information. Therefore, that variable passed to this particular call of 
 * setData() must not be eliminated when the call to setData() gets removed!
 **/
void rtsc_annotate_app_param(void* param);

/**
 * This annotation indicates that a particular parameter is a parameter
 * belonging to the operating system, so this parameter should be eliminiated 
 * when the OS API Calls of the source system are cleaned up.
 *
 * Example:
 * 
 * void setData(Message *m,void *data) {
 *   llvm_annotate_os_param(data);
 * }
 *
 * This indicates that this parameter does not carry application related
 * information. Therefore, the variable passed to this particular call to
 * setData() should also be eliminated when the call to setData gets removed!
 **/
void rtsc_annotate_os_param(void* param);

/**
 * This annotation indicates that all parameters passed to a parfticular system
 * call belong to the operating system, so all these parameters should be
 * eliminated when the OS API Calls of the source system are cleaned up.
 **/
void rtsc_annotate_os_param_all();

/******************************************************************************
 *                                                                            *
 * Annotations to mark access to global variables                             *
 *                                                                            *
 ******************************************************************************/

/**
 * This annotation marks the definition of a global variable
 **/
void RTSC_store_global(void *global,void *local);

/**
 * This annotation marks the use of a global variable
 **/
void RTSC_load_global(void *global,void *local);

#define STORE(GLOBAL,LOCAL)			\
  RTSC_store_global(&GLOBAL,&LOCAL)

#define LOAD(GLOBAL,LOCAL)			\
  RTSC_load_global(&GLOBAL,&LOCAL)

/******************************************************************************
 *                                                                            *
 * Annotations to provide information for WCET-analysis                       *
 *                                                                            *
 ******************************************************************************/

/**
 * Thist annotation provides the maximum number of iterations a loop will carry out
 **/
void RTSC_setLoopCount(unsigned int i);

/**
 * This annotation provides the maximum number of iteratiions a loop will carry
 * out at all as first parameter. The second parameter may hold a local variable
 * that contains more precise information about the actual iteration count
 **/
void RTSC_setVariableLoopCount(unsigned int i,void *var);

/**
 * Thist annotation provides the maximum depth of a recursive function call.
 **/
void RTSC_setRecursionDepth(unsigned int i);

/**
 * This annotation provides the maximum depth of a recursive function call as
 * first parameter. The second parameter may hold a local variable that contains
 * more precise information about the actual recursion depth.
 **/
void RTSC_setVariableRecursionDepth(unsigned int i,void *var);

#define LOOP_COUNT(count)			\
  RTSC_setLoopCount(count)

#define VAR_LOOP_COUNT(count,var)		\
  RTSC_setLoopCount(count,(void*)&var))

#define RECURSION_DEPTH(depth)			\
  RTSC_setRecursionDepth(depth)

#define VAR_RECURSION_DEPTH(depth,var)		\
  RTSC_setRecursionDepth(depth,(void*)&var)

/******************************************************************************
 *                                                                            *
 * Annotations to provide possible values for given variables                 *
 *                                                                            *
 ******************************************************************************/

/**
 * This annotation informs about possible values of the variable that is given
 * as first parameter. If such an annotation is given, no values except those
 * given by these annotations are considered.
 **/
void RTSC_possibleValue(void *var,void *val);

#define POSSIBLE_VAL(var,val)			\
  RTSC_possibleValue((void*)&var,(void*)val)

/**
 * Specify the WCET for a given basic block. If multiple annotations are given
 * the WCETs are summed up.
 **/
void RTSC_setBBWCET(unsigned int wcet);

#define BBWCET(WCET)				\
  RTSC_setBBWCET(WCET)

#endif /* __rtsc_annotate_h__ */
