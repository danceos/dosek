dOSEK v1.1
==========

Event Support
-------------

dOSEK now supports OSEK events! Events are the only possibility for an
task to wait actively for a condition. Events do always belong to a
task and can be set by any other task in the system. Events can also
be set by an alarm. dOSEK supports events in an unencoded and an
encoded variant.

For the GCFG construction, only the symbolic system execution can cope
with events. The system state flow pass is disabled if events are
present in the system.

With this change, dOSEK covers the most important system calls from
the conformance class ECC1.

Finite State Machine System Calls
----------------------------------

Usage: -a posix --generator-args "--syscalls fsm"

Using finite state machines to implement the operating system's
function is similar to system call specialization. We replace the
inner logic (scheduler, events, resources) of the OSEK system, with a
customized state machine. This state machine is constructed from the
state-transition graph (result of SSE). Each system-call site
corresponds to one input event in the FSM.

ARM Support
-----------

The ARM support was majorly improved. dOSEK can now run on the
ZedBoard plattform. Encoding of the system is as well supported as
system call specialization. Memory protection support is still
missing.


Dependability Measures
----------------------

- OS State Replication
- Retry Scheduling operations on ANB errors

Concurrent Dependability Service
--------------------------------

The dependability service runs on a seperate processor and checks
specially annotated data objects concurrently. The dataobjects are
declared in the OIL file:

    CHECKEDOBJECT area {
       TYPEDEF = chararray;
       HEADER = "app/bcc1/depsvc/type.h";
    };

During an explicit acquisition the data object can be modified. If the
dataobject is not acquired by the application, the dependability
service ensures the integrity with a checksum. For an working example,
see: app/bcc1/depsvc




