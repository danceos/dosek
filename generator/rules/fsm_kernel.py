from generator.rules.simple import SimpleSystem, AlarmTemplate
from generator.elements import CodeTemplate, Include, VariableDefinition, \
    Block, Statement, Comment, Function, Hook, DataObject
from generator.graph.AtomicBasicBlock import S, AtomicBasicBlock
from generator.graph.Resource import Resource
from generator.graph.Subtask import Subtask
from generator.graph.Function import Function


class FSMSystem(SimpleSystem):
