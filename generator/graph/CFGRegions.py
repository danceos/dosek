from generator.graph.Analysis import Analysis
from generator.graph.AtomicBasicBlock import E, S
from generator.elements import DataObject, Include
import logging

class CFGRegions(Analysis):
    """Generates assertions that are inserted before each system call to
    track the control flow within the system. For this markes in
    dominators are inserted and in dominated syscalls checked.

    """

    pass_alias = "cfg-regions"

    maximal_regions = 32

    def __init__(self):
        Analysis.__init__(self)
        self.regions     = None
        self.region_mask = None
        self.enter_mask  = None
        self.leave_mask  = None
        self.check_mask  = None

        self.marker_dataobject = None

    def requires(self):
        return ["dom-tree-system"]

    def select_interesting_regions(self):
        # Get all dominance regions
        dominance_pass = self.system_graph.get_pass("dom-tree-system")

        interesting_regions = []
        for each in dominance_pass.syscall_dominance_regions():
            # We can only do control flow tracking with regions that
            # are of size >1
            if len(each) == 1:
                continue
            # The whole system dominance region is also a subregion of
            # it self: skip it, since all blocks are dominated by StartOS
            if each.root.isA(S.StartOS):
                continue
            interesting_regions.append(each)

        # Sort Regions by size
        interesting_regions = sorted(interesting_regions, key = lambda x: len(x))

        # We only support a limited count of regions, therefore limit
        # the regions
        interesting_regions = interesting_regions[:self.maximal_regions]
        return interesting_regions

    def generate_regions(self, interesting_regions):
        self.regions     = {}
        self.region_mask = {}
        region_mask = 1
        for region in interesting_regions:
            region_id = "CFG_REGION_ABB%d" %(
                region.root.abb_id,
            )
            self.regions[region_id] = region
            self.region_mask[region_id] = region_mask
            # Generate new mask for next region
            region_mask <<= 1

    def generate_bitmasks(self):
        """Generates the enter/check/leave bitmasks"""
        self.enter_mask = {}
        self.leave_mask = {}
        self.check_mask = {}
        for syscall in self.system_graph.get_syscalls():
            if not syscall.syscall_type.isRealSyscall():
                continue
            self.check_mask[syscall] = []
            self.leave_mask[syscall] = []

            for region_id, region in list(self.regions.items()):
                if syscall.function.subtask and syscall.function.subtask.is_isr:
                    # Syscalls in interrupts should not be instrumented!
                    continue

                if region.root == syscall:
                    # In an ABB always only one region can be entered
                    assert not syscall in self.enter_mask
                    self.enter_mask[syscall] = [region_id]

                if syscall in region:
                    self.check_mask[syscall].append(region_id)
                else:
                    self.leave_mask[syscall].append(region_id)


    def get_mask(self, abb, _type):
        ret = None
        if _type == "enter":
            ret = self.enter_mask.get(abb, [])
        elif _type == "leave":
            ret = self.leave_mask[abb]
        elif _type == "check":
            ret = self.check_mask[abb]
        assert not ret is None, "Invalid argument"
        return "(" + " | ".join(["0"] + ret) + ")"

    def do(self):
        # Select interesting regions
        interesting_regions = self.select_interesting_regions()
        logging.info(" + generate checks for %d regions", len(interesting_regions))

        # Generate identifiers and bitmasks for regions
        self.generate_regions(interesting_regions)

        # Generate enter/check and leave masks
        self.generate_bitmasks()

        #for each in self.system_graph.get_syscalls():
        #    if not each.syscall_type.isRealSyscall():
        #        continue
        #    print each
        #    print self.get_mask(each, "enter")
        #    print self.get_mask(each, "leave")
        #    print self.get_mask(each, "check")



    # Functions that are called as callbacks in the generation process
    ##################################################################

    def generate_dataobjects(self, generator):
        generator.source_file.includes.add(Include("os/cfg-regions.h"))

        # Generate DataObject that holds the curren region mask
        self.marker_dataobject = DataObject("uint32_t", "OS_CFG_REGION_MASK")
        generator.source_file.data_manager.add(self.marker_dataobject)

        for region in self.regions:
            const = DataObject("const uint32_t", region, str(self.region_mask[region]))
            const.allocation_prefix = "constexpr "
            generator.source_file.data_manager.add(const)

    def system_enter_hook(self, generator, abb, hook):
        """This function is called by the code generation, when the system
           enter hook should be filled"""
        if abb.function.subtask.is_isr:
            # Syscalls in interrupts should not be instrumented!
            return

        enter_mask = self.get_mask(abb, "enter")
        check_mask = self.get_mask(abb, "check")
        leave_mask = self.get_mask(abb, "leave")

        generator.os_rules.call_function(hook, "os::CFGRegion::check", "void",
                                         [self.marker_dataobject.name,
                                          enter_mask, check_mask,
                                          leave_mask])
