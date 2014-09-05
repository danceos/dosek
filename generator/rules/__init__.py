assert __name__ == "generator.rules"

from generator.rules.base import BaseRules
from generator.rules.simple import SimpleSystem
from generator.rules.encoded import EncodedSystem
from generator.rules.unencoded import UnencodedSystem
from generator.rules.syscalls_full import FullSystemCalls
from generator.rules.syscalls_specialized import SpecializedSystemCalls
from generator.rules.x86 import X86Arch
from generator.rules.arm import ARMArch
from generator.rules.posix import PosixArch
