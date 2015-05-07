#!/usr/bin/python

import struct
import imp
import re
from gzip import GzipFile
from optparse import OptionParser
from generator.stats_binary import read_symbols, read_regions, Symbol
from generator.statistics import Statistics
from collections import namedtuple
from random import randint


def open_trace(filename):
    f = open(filename, "rb")
    if ord(f.read(1)) == 0x1f and ord(f.read(1)) == 0x8b:
        f.seek(0,0)
        return GzipFile(fileobj = f)
    f.seek(0,0)
    return f

def read_trace(trace_plugin_filename, trace_filename):
    """Generator that iterates over all events in trace"""

    trace_plugin = imp.load_source("trace", trace_plugin_filename)
    trace_file = open_trace(trace_filename)
    trace_event = trace_plugin.Trace_Event()

    acctime = 0
    while True:
        # Read trace length
        try:
            lengthNO = trace_file.read(4)
            if len(lengthNO) == 0:
                break
        except IOError:
            print "Could not read data from file"

        # Read Trace-Event
        length = struct.unpack('!I', lengthNO)[0]
        trace_event.ParseFromString(trace_file.read(length))

        # More compact dump for traces:
        if trace_event.HasField("time_delta"):
            acctime += trace_event.time_delta

        yield (acctime, trace_event)
    trace_file.close()


class SymbolMap(dict):
    """The Symbol map maps memory addresses to symbols for fast
    translation"""
    def __init__(self, symbols):
        symbols.append(Symbol(addr = 0, size = 1, name = "__OS_syscall_OSEKOS_IncrementCounter",
                              type = "OBJECT"))
        self.symbols = symbols
        for symbol in symbols:
            if not symbol.size:
                self[symbol.addr] = symbol
                self[symbol.name] = symbol


        for symbol in symbols:
            if symbol.size:
                for i in range(symbol.addr, symbol.addr+symbol.size):
                    self[i] = symbol
                    self[symbol.name] = symbol

class dOSEKDetector:
    START  = 1
    WITHIN = 2
    END    = 4

    def __init__(self, symbol_map):
        self.symbol_map = symbol_map
        self.syscall_endurance = set()
        self.syscall_end = set()

        for symbol in self.symbol_map.symbols:
            start = symbol.addr
            end   = symbol.addr+1
            if symbol.size:
                end = symbol.addr + symbol.size
            # All interrupt handlers are part of the system
            if symbol.name.startswith("irq_") \
               or symbol.name.startswith("isr_") \
               or symbol.name == "handler_exit" \
               or symbol.name == "sysenter_syscall":
                self.syscall_endurance.update(range(start, end))

            if symbol.name.startswith("__OS_"):
                self.syscall_endurance.update(range(start, end))

            if symbol.name == "irq_resume":
                self.syscall_end.add(start)

            if symbol.name.startswith(".asm_label.syscall_end"):
                # We do -1 here, because there is always a one byte
                # nop before the end marker and we want to capture
                # that one
                self.syscall_end.add(start-1)

            # When the scheduler is not inline, it will appear as a single function
            if ("Reschedule" in symbol.name and "Scheduler" in symbol.name):
                self.syscall_endurance.update(range(start, end))

            # Systemcall markers
            if symbol.name.startswith(".asm_label.syscall_start"):
                # Find end marker
                end_name = symbol.name.replace("syscall_start",
                                               "syscall_end")
                # Remove number at the end (that is a unique number)
                (end_name, count) = re.subn("_[0-9]*$", "", end_name)
                end_symbol = None
                for end in self.symbol_map.symbols:
                    if not end.addr >= symbol.addr:
                        continue
                    if end.name.startswith(end_name):
                        if not end_symbol or end.addr < end_symbol.addr:
                            end_symbol = end
                if not end_symbol:
                    continue
                zone = range(symbol.addr, end_symbol.addr)
                #print symbol
                #print end_symbol
                #print zone
                self.syscall_endurance.update(zone)
                for addr in zone:
                    self.symbol_map[addr] = symbol

    def for_addr(self, addr):
        ret = 0
        if addr in self.syscall_endurance:
            ret |= self.WITHIN
        if addr in self.syscall_end:
            ret |= self.END
        if ret == 0:
            if self.symbol_map.get(addr) is None:
                ret |= self.WITHIN
        return ret

    def classify(self, last_addr, current_addr, next_addr):
        this = self.for_addr(current_addr)
        if this:
            before = self.for_addr(last_addr)
            after  = self.for_addr(next_addr)
            if before == 0:
                this |= self.START
            if before & self.END:
                this |= self.START
            if after == 0:
                this |= self.END
            if after & self.START:
                this |= self.END
        return this

class SyscallRegion:
    def __init__(self, start_time):
        self.start_time = start_time
        self.trace      = []
        self.end_time   = start_time

    def contains(self, symbol):
        for x in self.trace:
            if x[1].name == symbol:
                return True
        return False

    def indexOf(self, name):
        for i in range(0, len(self.trace)):
            if self.trace[i][1].name == name:
                return i
        assert False, "Symbol could not find symbol " + str(self.trace)

    def insert_after(self, name, symbol):
        for i in range(0, len(self.trace)):
            if self.trace[i][1].name == name:
                self.trace.insert(i+1, (0, symbol))
                return
        assert False, "Symbol could not be inserted " + str(self.trace)

    def push_symbol(self, time, symbol):
        if not self.trace or self.trace[-1][1] != symbol:
            self.trace.append([1, symbol])
        else:
            self.trace[-1][0] += 1
        # Increase time
        if time:
            assert time >= self.end_time
            self.end_time = time

    @property
    def names(self):
        return [x[1].name for x in self.trace]

def syscall_regions(trace_events, symbol_map):
    """Generator that returns detected syscall regions"""
    last_addr = current_addr = next_addr = None
    detector = dOSEKDetector(symbol_map)

    region = None

    for time, event in trace_events:
        if event.HasField("memaddr"):
            continue
        # Read one event ahead and preserve one old event
        last_addr    = current_addr
        current_addr = next_addr
        next_addr = event.ip

        # When "pipeline" is full
        if last_addr:
            classified = detector.classify(last_addr, current_addr, next_addr)
            # print hex(current_addr), classified, symbol_map.get(current_addr)
            # If event has no class, simply continue
            if classified == 0:
                continue
            symbol = symbol_map.get(current_addr)
            if classified & detector.START:
                assert region is None, region
                region = SyscallRegion(time)

            # Symbol is part of the current region
            region.push_symbol(time, symbol)

            # We are a generator, therefore we yield the current
            # syscall region
            if classified & detector.END:
                if region.contains("irq_48"):
                    region.insert_after("irq_48", symbol_map["__OS_syscall_OSEKOS_IncrementCounter"])
                yield region
                region = None


def cut_out_timer_interrupt(region):
    if region.contains("irq_48") and region.contains("handler_exit"):
        start = region.indexOf("irq_48")
        end   = region.indexOf("handler_exit")
        if start == 0:
            # Is a pure interrupt region
            assert end == len(region.trace) - 1 or region.names[end+1].startswith("irq_"), region.names # Dispatch over AST
            return region, None
        isr_trace = region.trace[start:end+1]
        syscall_trace = list(region.trace)
        del syscall_trace[start:end+1]

        syscall_region = SyscallRegion(region.start_time)
        isr_region = SyscallRegion(region.start_time)
        syscall_region.end_time = isr_region.end_time = region.end_time
        syscall_region.trace = syscall_trace
        isr_region.trace = isr_trace
        return syscall_region, isr_region

    return region, None


def main(options, args):
    symbols = [x for x in read_symbols(options.elf, options.nm)
               if x.addr]
    symbol_map = SymbolMap(symbols)

    trace_events = read_trace(options.traceplugin, options.trace)
    stats = Statistics.load(options.stats)
    for abb in stats.find_all("AtomicBasicBlock").values():
        if not 'generated-function' in abb:
            continue
        abb["activations"] = []
    sysgraph = stats.find_all("SystemGraph").values()[0]
    IncrementCounter = {"_id": id(main),
                         "_type": "AtomicBasicBlock", 
                         "_name": "ABB-10/IncrementCounter",
                         "generated-function": ["__OS_syscall_OSEKOS_IncrementCounter"],
                         "activations": [],
                        "symbols": []}
    sysgraph["alarms"] = [IncrementCounter]
    stats.rebuild_index(sysgraph)

    region_iterator = iter(syscall_regions(trace_events, symbol_map))
    delayed_regions = []
    regions_count = 0


    while region_iterator or len(delayed_regions):
        regions_count += 1
        if region_iterator:
            try:
                syscall_region = next(region_iterator)
            except StopIteration:
                region_iterator = None
                print "trace-analyze: Processing %d delayed interrupt regions" %(len(delayed_regions))
                continue
            syscall_region, interrupt_region = cut_out_timer_interrupt(syscall_region)
            if interrupt_region:
                delayed_regions.append(interrupt_region)
        else:
            syscall_region = delayed_regions.pop()

        names = [x[1].name for x in syscall_region.trace if x[1]]
        region_length = sum([x[0] for x in syscall_region.trace])
        event_type = None
        # fixup names with asm labels
        for i in range(0, len(names)):
            if ".asm_label.syscall_start" in names[i]:
                m = re.subn("^.asm_label.syscall_start_(.*)_[0-9]+$", "\\1", names[i])
                names[i] = m[0]

        for name in names:
            if "__OS_syscall" in name:
                assert event_type  is None, (names, event_type, options.stats)
                event_type = name
            if name in ("__OS_StartOS_dispatch"):
                assert event_type  is None, (names, options.stats)
                event_type = name
                break

        # If it does not contain a syscall, use the userland function
        # names (e.g. the start end markers)
        if event_type == None:
            for name in names:
                if "OSEKOS" in name and "__ABB" in name:
                    # Might also be an ISR
                    assert event_type  is None or "irq_handler" in names[0], names
                    event_type = name

        for abb in stats.find_all("AtomicBasicBlock").values():
            if not 'generated-function' in abb:
                continue
            if event_type in abb["generated-function"]:
                trace_info = {
                    "cycles": region_length,
                    "trace": [(x[0], x[1].name) for x in syscall_region.trace],
                    "start-time": syscall_region.start_time,
                    "end-time": syscall_region.end_time,
                }
                abb["activations"].append(trace_info)

        if event_type == "__OS_syscall_OSEKOS_IncrementCounter":
            IncrementCounter["symbols"] = list(set(IncrementCounter["symbols"]) |  set(names))

    print "Processed %d Systemcalls" % regions_count
    IncrementCounter["generated-codesize"] = 0
    for symbol in IncrementCounter["symbols"]:
        if symbol in symbol_map:
            symbol = symbol_map[symbol]
            if symbol.size:
                IncrementCounter["generated-codesize"] += symbol.size
    print options.stats
    stats.save(options.stats)


if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-e", "--elf", dest="elf",
                      help="elf binary", metavar="ELF")
    parser.add_option("-t", "--trace", dest="trace",
                      help="trace.pb", metavar="TRACE")
    parser.add_option("-o", "--objdump", dest="objdump", default="/usr/bin/objdump",
                      help="objdump binary location", metavar="OBJDUMP")
    parser.add_option("-p", "--trace-plugin", dest="traceplugin",
                      help="python trace plugin path", metavar="OBJDUMP")
    parser.add_option("", "--stats-dict", dest="stats",
                      help="stats.dict.py path", metavar="STATS")
    parser.add_option("", "--nm", dest="nm", default="/usr/bin/nm",
                      help="nm binary location", metavar="NM")


    (options, args) = parser.parse_args()

    try:
        main(options, args)
    except RuntimeError as e:
        print(e)
        print(options.stats)
