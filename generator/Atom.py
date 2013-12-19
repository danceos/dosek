#!/usr/bin/python

class Atom:
    """Base class for all atoms"""
    def __init__(self):
        pass

    @classmethod
    def isa(cls, atom):
        assert type(atom) == dict, str(atom)
        return issubclass(atom["__token"], cls)

    def generate_into(self, generator, function_block):
        raise Exception("generate into not defined for " + self.__class__.__name__)

