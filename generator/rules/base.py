#!/usr/bin/python

from generator.tools import stringify
from generator.elements import *

class BaseRules:
    def __init__(self):
        self.generator = None

    def set_generator(self, generator):
        self.generator = generator

    def call_function(self, block, function, rettype, arguments):
        """Generates a call to a function and stores the result in an
           variable, if it isn't void"""
        ret_var = block.add( VariableDefinition.new(self.generator, rettype))
        call    = block.add( FunctionCall(function, arguments, ret_var.name))
        return ret_var

    def return_statement(self, block, expression):
        block.add(Statement("return %s" % expression))


    def object_COM(self, interface="COM1"):
        """Returns a variable name to a serial output driver, which can be used for
        debug printing"""
        varname = self.generator.variable_name_for_singleton("Serial", interface)
        serial = DataObject("Serial", varname, "Serial(Serial::%s)" % interface)
        self.generator.source_file.data_manager.add(serial)
        self.generator.source_file.includes.add(Include("serial.h"))
        return varname

    def kout(self, block, *expressions):
        """Generates a print statement to a serial console"""
        com = self.object_COM()
        block.add( Statement("%s << %s" % (com, " << ".join(expressions))))

    def system_enter_hook(self, function):
        hook = Hook("SystemEnterHook")
        function.add(hook)
        return hook

    def system_leave_hook(self, function):
        hook = Hook("SystemLeaveHook")
        function.add(hook)
        return hook

    def systemcall(self, systemcall, function):
        """Generate systemcall into function"""
        self.system_enter_hook(function)

        ret_var = self.call_function(function,
                                     "OSEKOS_" + systemcall.function,
                                     systemcall.rettype,
                                     [x[0] for x in systemcall.arguments])

        self.kout(function, stringify(systemcall.function + "was called\n"))
        self.system_leave_hook(function)

        if ret_var:
            self.return_statement(function, ret_var.name)


    def StartOS(self, block):
        pass
