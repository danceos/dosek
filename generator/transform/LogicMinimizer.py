from generator.analysis import Analysis
from collections import namedtuple, defaultdict
from .FiniteStateMachineBuilder import FiniteStateMachine, Transition, Event
import math
import os
import subprocess
import logging

class LogicMinimizer(Analysis):
    def __init__(self):
        super(LogicMinimizer, self).__init__()

    def requires(self):
        return ["fsm"]

    def do(self):
        fsm = self.system_graph.get_pass("fsm").fsm.copy()

        self.fsm = self.call_nova(fsm)

    def call_nova(self, fsm):
        class isr_renamer:
            def __init__(self):
                self.mapping = {}
                self.__i = 1
            def __call__(self, action):
                if action.conf.is_isr:
                    return 0
                    #return None
                else:
                    if not action in self.mapping:
                        self.mapping[action] = self.__i
                        self.__i += 1
                    return self.mapping[action]
            def max_int(self):
                return self.__i

        isr_rename = isr_renamer()
        fsm.rename(events = True, actions = isr_rename)

        # Generate Bitstrings
        class binstring_renamer:
            def __init__(self, max_items, prefix = ''):
                self.bitwidth = math.ceil(math.log2(max_items))
                self.__i = 0
                self.prefix = prefix
            def __call__(self, x):
                if type(x) == int:
                    l = x
                elif x == None:
                    return "-" * self.bitwidth
                else:
                    l = self.__i
                    self.__i += 1
                return "{2}{0:0{1}b}".format(l, self.bitwidth, self.prefix)

        event_rename = binstring_renamer(len(fsm.events), 'e')
        state_rename = binstring_renamer(len(fsm.states), 's')
        action_rename = binstring_renamer(isr_rename.max_int())

        # Rename to Bitstring
        fsm.rename(events = event_rename,
                   states = state_rename,
                   actions = action_rename)

        nova_input = "%snova.fsm" % self.system_graph.basefilename
        with open(nova_input, "w+") as fd:
            fd.write(".i {0}\n".format(event_rename.bitwidth))
            fd.write(".o {0}\n".format(action_rename.bitwidth))
            fd.write(".s {0}\n".format(len(fsm.states)))
            fd.write(".symbolic input\n".format(len(fsm.states)))

            fd.write(str(fsm) + "\n")
            fd.write(".e\n")

        stdout = subprocess.check_output(["nova", nova_input]).decode('ascii', 'ignore')
        event_mapping = {}
        state_mapping = {}
        for line in stdout.split("\n"):
            if line.startswith(".code"):
                (_, old, new) = line.split()
                if old.startswith("e"):
                    event_mapping[old] = new
                elif old.startswith("s"):
                    state_mapping[old] = new
                else:
                    assert False, "Invalid NOVA output"

        # No event encoding is used twice
        assert len(event_mapping) == len(fsm.events)
        assert len(event_mapping) == len(set(event_mapping.values()))

        # No state is given doubled
        assert len(state_mapping) == len(fsm.states)
        assert len(state_mapping) == len(set(state_mapping.values()))
        fsm.rename(events = lambda e: event_mapping[e],
                   states = lambda s: state_mapping[s])

        event_len = len(fsm.events[0].name)
        state_len = len(fsm.initial_state)
        action_len = action_rename.bitwidth
        self.event_len, self.state_len, self.action_len \
            = (event_len, state_len, action_len)

        self.truth_table = []
        # Read in the minimzed truth table
        with open("%s.esp" % nova_input) as esp:
            for line in esp.readlines():
                line = [x for x in line if x in "01-"]
                if len(line) == event_len + state_len * 2 + action_len:
                    input_word = line[0:event_len+state_len]; del line[0:event_len+state_len]
                    output_state = line[0:state_len]; del line[0:state_len]
                    output_action = line

                    # Generate pattern and mask
                    mask_filter = {'0': '1', '1': '1', '-': '0'}
                    pattern_filter = {'0': '0', '1': '1', '-': '0'}
                    mask_word = [mask_filter[x] for x in input_word]
                    pattern_word = [pattern_filter[x] for x in input_word]

                    self.truth_table.append(("".join(mask_word), "".join(pattern_word),
                                             "".join(output_state), "".join(output_action)))

        matches = [0 for x in self.truth_table]
        for transition in fsm.transitions:
            input_word = int(transition.event+transition.source, 2)
            desired_output_word = int(transition.target+transition.action, 2)
            got_output_word = 0
            for i, (mask_word, pattern_word, output_state, output_action) in enumerate(self.truth_table):
                output_word = int(output_state+output_action, 2)
                mask_word = int(mask_word, 2)
                pattern_word = int(pattern_word, 2)
                if (input_word & mask_word) == pattern_word:
                    got_output_word |= output_word
                    matches[i] += 1
            assert got_output_word == desired_output_word
        logging.info("%d lines in minimzed truth table", len(self.truth_table))
        return fsm
