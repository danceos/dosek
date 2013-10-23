#!/usr/bin/python

from lxml import objectify
import os

class RTSCAnalysis:
    """The RTSCAnalysis class represents the results of the application
analysis done by the RTSC. Informations are for example for every
system call: Who called it? In which ABB?"""
    def __init__(self, rtsc_xml):
        self.rtsc_xml   = rtsc_xml
        self.rtsc_dom   = objectify.parse(open(self.rtsc_xml)).getroot()

    def syscalls(self):
        """Return all system calls"""
        return [self.SystemCall(x) for x in self.rtsc_dom.systemcall]

    def find_syscall(self, abbid):
        """Find a specific system call within an ABB"""
        for syscall in self.rtsc_dom.systemcall:
            if abbid == int(syscall.calling.get("abb")):
                return self.SystemCall(syscall)

    class SystemCall:
        def __init__(self, xml):
            self.xml = xml
        def name(self):
            return self.xml.get("name")
        def calling_task(self):
            return self.xml.calling.task
        def calling_subtask(self):
            return self.xml.calling.subtask
        def calling_event(self):
            return self.xml.calling.event


################################################################
##
## Testcases
##
################################################################
import unittest

class TestRTSCAnalysis(unittest.TestCase):
    def setUp(self):
        self.rtsc = RTSCAnalysis("test/rtsc_analyze.xml")
    def test_osek_attributes(self):
        syscall = self.rtsc.find_syscall(0)
        self.assertEqual(syscall.name(), "OSEKOS_ActivateTask")
        self.assertEqual(syscall.calling_task(), "Event1")
        self.assertEqual(syscall.calling_event(), "Event1")
        self.assertEqual(syscall.calling_subtask(), "Handler11")



if __name__ == "__main__":
    unittest.main()
