#!/usr/bin/python

from lxml import objectify

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
        syscalls = []
        for x in self.rtsc_dom.systemcall:
            args = []
            for arg in x.xpath("*[local-name()='call_arguments']/*[local-name()='arg']"):
                args += [str(arg)]
            syscall = self.SystemCall(name = x.get("name"),
                                      abb  = int(x.get("abb")),
                                      arguments = args)
            syscalls.append(syscall)
        return syscalls

    def find_syscall(self, abbid):
        """Find a specific system call within an ABB"""
        for syscall in self.syscalls():
            if abbid == syscall.abb:
                return syscall

    SystemCall = namedtuple("SystemCall", ["name", "abb", "arguments"])

    def get_abbs(self):
        abbs = []
        # Gather all ABB xml nodes under <abbgraph>
        for abb_xml in self.rtsc_dom.xpath('//*[local-name()=\'abb\']'):
            abb = self.ABB(id = int(abb_xml.get("name")),
                           in_function=abb_xml.get("function"),
                           func_entry = abb_xml.get("func_entry") == "true")
            abbs.append(abb)
        return abbs

    def get_edges(self):
        # Gather all ABB xml nodes under <abbgraph>
        deps = []
        for abb_xml in self.rtsc_dom.xpath('//*[local-name()=\'abb\']'):
            for dep_xml in abb_xml.xpath('*[local-name()=\'dependency\']'):
                dep = self.Dependency(source = int(abb_xml.get("name")),
                                 target = int(dep_xml.get("target")))
                deps.append(dep)
        return deps

    def get_calls(self):
        # Gather all ABB xml nodes under <abbgraph>
        calls = []
        for call_xml in self.rtsc_dom.xpath('*[local-name()=\'functioncall\']'):
            call = self.Call(function = call_xml.get("name"),
                             abb = int(call_xml.get("abb")))
            calls.append(call)
        return calls

    ABB = namedtuple('ABB', ['id', 'in_function', 'func_entry'])
    Dependency = namedtuple('Dependency', ['source', 'target'])
    Call = namedtuple('Call', ['function', 'abb'])

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
        syscall = self.rtsc.find_syscall(4)
        self.assertEqual(syscall.name, "OSEKOS_ActivateTask")
        self.assertEqual(syscall.abb, 4)
        self.assertEqual(syscall.arguments[0], "OSEKOS_TASK_Struct_Handler13")


if __name__ == "__main__":
    unittest.main()
