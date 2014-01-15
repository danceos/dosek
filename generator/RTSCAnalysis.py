#!/usr/bin/python

from lxml import objectify
import os

from collections import namedtuple

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

    def get_abbs(self):
        abbs = []
        # Gather all ABB xml nodes under <abbgraph>
        for abb_xml in self.rtsc_dom.xpath('//*[local-name()=\'abb\']'):
            abb = self.ABB(id = int(abb_xml.get("name")),
                           in_function=abb_xml.get("infunction"),
                           guard = abb_xml.get("guard"),
                           func_entry = abb_xml.get("func_entry") == "true")
            abbs.append(abb)
        return abbs

    def get_edges(self):
        # Gather all ABB xml nodes under <abbgraph>
        deps = []
        for abb_xml in self.rtsc_dom.xpath('//*[local-name()=\'abb\']'):
            for dep_xml in abb_xml.xpath('*[local-name()=\'dependency\']'):
                dep = self.Dependency(source = int(abb_xml.get("name")),
                                 target = int(dep_xml.get("target")),
                                 type = dep_xml.get("type"))
                deps.append(dep)
        return deps

    ABB = namedtuple('ABB', ['id', 'in_function', 'guard', 'func_entry'])
    Dependency = namedtuple('Dependency', ['source', 'target', 'type'])

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
