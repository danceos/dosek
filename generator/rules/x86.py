from generator.rules.base import BaseRules
from generator.elements import CodeTemplate

class X86Arch(BaseRules):
    def __init__(self):
        BaseRules.__init__(self)

    def generate_linkerscript(self):
        linker_script = LinkerScriptTemplate(self)
        with self.generator.open_file("linker.ld") as fd:
            content = linker_script.expand()
            fd.write(content)


class LinkerScriptTemplate(CodeTemplate):
    def __init__(self, x86):
        CodeTemplate.__init__(self, x86.generator, "arch/i386/linker.ld.in")
        self.x86 = x86
        self.system_graph    = self.x86.system_graph
        # Reference to the objects object of our rule system
        self.objects = self.x86.objects
        # Link the foreach_subtask method from the rules
        self.foreach_subtask = self.x86.foreach_subtask

        assert len(self.system_graph.get_subtasks()) <= 8, "paging.h does not support more tasks atm"

    def __select_statement(self, symbol, sections, library="*"):
        """Returns a newline seperated string of linker selectiors, for the
        corresponding sections"""
        ret = ""
        for sec in sections:
            ret += '%s(".%s.%s");\n' %(library, sec, symbol)
        return ret

    def task_code_regions(self, snippet, args):
        def do(subtask):
            ret = ". = ALIGN(4096);\n"
            ret += "_stext_task%s = .;\n" % self.objects[subtask]["task_id"]
            # Find all functions that belong to the function
            for function in self.system_graph.functions.values():
                if subtask == function.subtask:
                    ret += self.__select_statement(function.function_name, ["text", "rodata"])
            for function in self.objects[subtask]["generated_functions"]:
                ret += self.__select_statement(function.function_name, ["text", "rodata"])

            ret += "_etext_task%s = .;\n" % self.objects[subtask]["task_id"]
            ret += "\n"
            return ret

        return self.foreach_subtask(do)

    def task_stacks(self, snippet, args):
        def do(subtask):
            ret = ". = ALIGN(4096);\n"
            ret += "_sstack_task%s = .;\n" % self.objects[subtask]["task_id"]
            ret += self.__select_statement(self.objects[subtask]["stack"].name, ["data"])
            ret += "_estack_task%s = .;\n" % self.objects[subtask]["task_id"]
            ret += "\n"
            return ret

        return self.foreach_subtask(do)

    def task_data(self, snippet, args):
        def do(subtask):
            ret = ". = ALIGN(4096);\n"
            ret += "_sdata_task%s = .;\n" % self.objects[subtask]["task_id"]
            ret += self.__select_statement(subtask.name + "*", ["data"])
            ret += "_edata_task%s = .;\n" % self.objects[subtask]["task_id"]
            ret += "\n"
            return ret

        return self.foreach_subtask(do)

