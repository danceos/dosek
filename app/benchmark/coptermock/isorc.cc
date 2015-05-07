#include "os.h"
#include "fail/trace.h"

//typedef struct spi_reply_message {
//    TaskType event1_task;
//    EventMaskType event1_mask;
//    TaskType event2_task;
//    EventMaskType event2_mask;
//} spi_reply_message_t;

DeclareResource(SPIBusResource);

DeclareAlarm(SamplingAlarm);
DeclareAlarm(SignalGatherTimeoutAlarm);
DeclareAlarm(ActuateAlarm);
DeclareAlarm(CopterControlWatchdogAlarm);

DeclareEvent(CopterControlReceiveEvent);
DeclareEvent(MavMsgReceiveEvent);
DeclareEvent(EthernetReceiveEvent);
DeclareEvent(SPIReceiveEvent);
DeclareEvent(SignalGatherAnalogEvent);
DeclareEvent(SignalGatherDigital1Event);
DeclareEvent(SignalGatherDigital2bEvent);
DeclareEvent(SignalGatherDigital2aEvent);
DeclareEvent(SignalGatherDigital1TimeoutEvent);
DeclareEvent(SignalGatherDigital2bTimeoutEvent);
DeclareEvent(SignalGatherDigital2aTimeoutEvent);
DeclareEvent(FlightControlActuateEvent);
DeclareEvent(FlightControlAttitudeEvent);

DeclareTask(InitTask);
DeclareTask(SignalGatherInitiateTask);
DeclareTask(SignalGatherWaitTask);
DeclareTask(SignalGatherTimeoutTask);
DeclareTask(SignalProcessingActuateTask);
DeclareTask(SignalProcessingAttitudeTask);
DeclareTask(FlightControlAttitudeTask);
DeclareTask(FlightControlActuateTask);
DeclareTask(ActuateTask);
DeclareTask(MavlinkSendTask);
DeclareTask(CopterControlWatchdogTask);
DeclareTask(CopterControlTask);
DeclareTask(EthernetTask);
DeclareTask(MavlinkRecvTask);

#ifdef CONFIG_ARCH_I386
#include "pit.h"
void StartupHook() {
	// generate interrupt @ 100 Hz (10ms)
	arch::PIT::set_periodic(100);
}
#endif



TEST_MAKE_OS_MAIN( StartOS(0) )

typedef enum {
	INIT_TASK = 0,
    SIGNAL_GATHERING_INITATE,
    SP_ACTUATE_TASK,
    SG_TIMEOUT_TASK,
    SP_ATTITUDE_TASK,
    SG_WAIT_TASK,
    SP_ACTUATE_TIMEOUT_TASK,
    SP_ATTITUDE_TIMEOUT_TASK,
    FC_ACTUATE_TASK,
    FC_ATTITUDE_TASK,
    ACTUATE_TASK = 10,
    ETH_INIT,
    ETH_PACKET,
    MAV_SEND,
    MAV_RECV,
    CC_CONTROL_TASK,
    CC_WATCHDOG_TASK,
    CC_WATCHDOG_TASK_PANIC,
    SHUTDOWN,
    PANIC_BUTTON = 0xffff,
} place;


static unsigned int time_counter = 0;

// logdata
// static const TaskType sp_att = SignalProcessingAttitudeTask,
//    sp_act = SignalProcessingActuateTask;

static int spi_reply_idx;

// static spi_reply_message_t logdata_signal_gathering_events[] = {
//     { sp_act, SignalGatherDigital2aEvent | SignalGatherDigital2bEvent,
//       sp_att, SignalGatherDigital1Event },
//     { sp_act, SignalGatherDigital2bEvent | SignalGatherDigital2aEvent,
//       sp_att, SignalGatherDigital1Event},
//     { sp_act, SignalGatherDigital2bEvent,
//       sp_att, SignalGatherDigital1Event},
//     { sp_act, SignalGatherDigital2aEvent,
//       sp_att, SignalGatherDigital1Event},
//     { sp_act, 0,
//       sp_att, SignalGatherDigital1Event},
//     { sp_act, SignalGatherDigital2bEvent | SignalGatherDigital2aEvent,
//       sp_att, 0},
//     { sp_act, 0,
//       sp_att, 0},
// };

//static int ethernet_events[] = { 1, 7, -1};

//#define test_trace(x) do { kout << time_counter << " " << (int) x << endl; } while(0)

// autostarted by dOSEK!
TASK(InitTask) {
    test_trace(INIT_TASK);

	// We set up a period alarm for initate the sampling task. This
    // Task runs every 3 ms. This activates the SignalGatherInitateTask.
    SetRelAlarm(SamplingAlarm, 100, 3);
    SetRelAlarm(ActuateAlarm, 103, 9);
    SetRelAlarm(CopterControlWatchdogAlarm, 100, 1);


    ActivateTask(EthernetTask);
    TerminateTask();
}


TASK(SignalGatherInitiateTask) {
    time_counter++;
    test_trace(SIGNAL_GATHERING_INITATE);

    // Our benchmark should do exactly  actuate rounds.
    if (time_counter >  3 * 3 + 1) {
		Machine::disable_interrupts();
        //CancelAlarm(SamplingAlarm);
        //CancelAlarm(ActuateAlarm);
        //CancelAlarm(CopterControlWatchdogAlarm);
        test_trace(SHUTDOWN);
		test_finish();
		ShutdownMachine();
    }

    // Activate the processing tasks, they clear their event masks
    // immediatly, and then go to sleep.
    ActivateTask(SignalProcessingActuateTask);
    ActivateTask(SignalProcessingAttitudeTask);

    // First of all we would sample our analog sensors, which is done
    // imediately. Therefore the event can be set.
    SetEvent(SignalProcessingAttitudeTask, SignalGatherAnalogEvent);

    // Before we send our data to "SPI", we set up a timeout alarm to
    // activate the signal processing after an exact time.
    CancelAlarm(SignalGatherTimeoutAlarm); // after 2 ms
    SetRelAlarm(SignalGatherTimeoutAlarm, 2, 0); // after 2 ms

    {
        GetResource(SPIBusResource);

		spi_reply_idx = (time_counter - 1) % 7;

        ReleaseResource(SPIBusResource);
    }

    //static int ethernet_events[] = { 1, 7, -1};
	if (time_counter == 1 | time_counter == 7) {
		SetEvent(EthernetTask, EthernetReceiveEvent);
	}

	ChainTask(SignalGatherWaitTask);
}

TASK(SignalGatherWaitTask) {
    test_trace(SG_WAIT_TASK);

	int reply;
    /* We use a ressource to lock the SPI bus */
    GetResource(SPIBusResource);
    /* Receive message from the "spi bus" */

	reply = spi_reply_idx;

	ReleaseResource(SPIBusResource);

	// static const TaskType sp_att = SignalProcessingAttitudeTask,
	// sp_act = SignalProcessingActuateTask;
	// static spi_reply_message_t logdata_signal_gathering_events[] = {
	// 0:	{ sp_act, SignalGatherDigital2aEvent | SignalGatherDigital2bEvent,
	//        sp_att, SignalGatherDigital1Event },

	// 1:	{ sp_act, SignalGatherDigital2bEvent | SignalGatherDigital2aEvent,
	//        sp_att, SignalGatherDigital1Event},

	// 2:	{ sp_act, SignalGatherDigital2bEvent,
	// 	  sp_att, SignalGatherDigital1Event},

	// 3:	{ sp_act, SignalGatherDigital2aEvent,
	// 	  sp_att, SignalGatherDigital1Event},

	// 4:	{ sp_act, 0,
	// 	  sp_att, SignalGatherDigital1Event},

	// 5:	{ sp_act, SignalGatherDigital2bEvent | SignalGatherDigital2aEvent,
	// 	  sp_att, 0},

	// 6:	{ sp_act, 0,
	// 	  sp_att, 0},
	// };

	// CHANGE: In dOSEK references to system objects cannot be
	// variable. Therefore we have to use a big switch case to emulate
	// the above table.
	if (reply <= 3) {
		CancelAlarm(SignalGatherTimeoutAlarm);
	}

	if (reply == 0 | reply == 1 | reply == 5) {
		SetEvent(SignalProcessingActuateTask, SignalGatherDigital2aEvent | SignalGatherDigital2bEvent);
	}
	
	if (reply <= 4) {
		SetEvent(SignalProcessingAttitudeTask, SignalGatherDigital1Event);
	}

	if (reply == 2)  {
		SetEvent(SignalProcessingActuateTask, SignalGatherDigital2bEvent);
	}

	if (reply == 3)  {
		SetEvent(SignalProcessingActuateTask, SignalGatherDigital2aEvent);
	}

    TerminateTask();
}

TASK(SignalGatherTimeoutTask) {
    test_trace(SG_TIMEOUT_TASK);
    SetEvent(SignalProcessingActuateTask, SignalGatherDigital2aTimeoutEvent | SignalGatherDigital2bTimeoutEvent);
    SetEvent(SignalProcessingAttitudeTask, SignalGatherDigital1TimeoutEvent);
    TerminateTask();
}


TASK(SignalProcessingActuateTask) {
    ClearEvent(SignalGatherDigital2aEvent
                   | SignalGatherDigital2bEvent
                   | SignalGatherDigital2aTimeoutEvent
                   | SignalGatherDigital2bTimeoutEvent);
    WaitEvent(SignalGatherDigital2aEvent
                  | SignalGatherDigital2bEvent
                  | SignalGatherDigital2aTimeoutEvent
                  | SignalGatherDigital2bTimeoutEvent);

    EventMaskType events;
    GetEvent(SignalProcessingActuateTask, &events);
    int not_timeout = events & (SignalGatherDigital2aEvent | SignalGatherDigital2bEvent);

    ClearEvent(SignalGatherDigital2aEvent
                   | SignalGatherDigital2bEvent
                   | SignalGatherDigital2aTimeoutEvent
                   | SignalGatherDigital2bTimeoutEvent);

    if (not_timeout) {
        test_trace(SP_ACTUATE_TASK);
    } else {
        test_trace(SP_ACTUATE_TIMEOUT_TASK);

    }

    ChainTask(FlightControlActuateTask);
}

TASK(SignalProcessingAttitudeTask) {
    ClearEvent(SignalGatherAnalogEvent | SignalGatherDigital1Event | SignalGatherDigital1TimeoutEvent);
    WaitEvent(SignalGatherDigital1Event | SignalGatherDigital1TimeoutEvent);
    WaitEvent(SignalGatherAnalogEvent);

    EventMaskType events;
    GetEvent(SignalProcessingAttitudeTask, &events);
    int not_timeout = events & SignalGatherDigital1Event;

    ClearEvent(SignalGatherAnalogEvent | SignalGatherDigital1Event | SignalGatherDigital1TimeoutEvent);

    if (not_timeout)
        test_trace(SP_ATTITUDE_TASK);
    else
        test_trace(SP_ATTITUDE_TIMEOUT_TASK);

    ChainTask(FlightControlAttitudeTask);
}

TASK(FlightControlActuateTask) {
    test_trace(FC_ACTUATE_TASK);
    TerminateTask();
}

TASK(FlightControlAttitudeTask) {
    test_trace(FC_ATTITUDE_TASK);
    TerminateTask();
}

TASK(ActuateTask) {
    test_trace(ACTUATE_TASK);
    ActivateTask(MavlinkSendTask);
    TerminateTask();
}


TASK(MavlinkSendTask) {
    test_trace(MAV_SEND);
    TerminateTask();
}


TASK(MavlinkRecvTask) {
    test_trace(MAV_RECV);
    ActivateTask(CopterControlTask);
    TerminateTask();
}


// CopterControl
int watchdog_timer;
TASK(CopterControlTask) {
    watchdog_timer = 0;
    test_trace(CC_CONTROL_TASK);
    TerminateTask();
}


TASK(CopterControlWatchdogTask) {
    watchdog_timer ++;
    if (watchdog_timer <= 25)
        test_trace(CC_WATCHDOG_TASK);
    else {
        test_trace(CC_WATCHDOG_TASK_PANIC);
    }
    TerminateTask();
}

TASK(EthernetTask) {
    test_trace(ETH_INIT);
    while(1) {
        WaitEvent(EthernetReceiveEvent);
        ClearEvent(EthernetReceiveEvent);
        test_trace(ETH_PACKET);
        ActivateTask(MavlinkRecvTask);
	}
	TerminateTask();
}

void FaultDetectedHook() {
	Machine::disable_interrupts();
	(void) arg1;
	(void) arg2;
	(void) type;

	// CHANGE: In dOSEK we cannot disable alarms in the
	// FaultDetectedHook, but we can disable interrupts
	//CancelAlarm(SamplingAlarm);
	//CancelAlarm(ActuateAlarm);
	//CancelAlarm(CopterControlWatchdogAlarm);
	test_trace(SHUTDOWN);

	ShutdownMachine();
}

